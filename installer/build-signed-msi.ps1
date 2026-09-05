<#
.SYNOPSIS
    Firma y empaqueta AgilEx by Marduk como MSI distribuible.

.DESCRIPTION
    Ejecuta seis etapas: preflight, verificacion de integridad, firma del
    ejecutable, empaquetado MSI, firma del MSI y compresion RAR. Genera
    REPORTE_FIRMA.txt como evidencia.

    El script no toma decisiones ni corrige errores: valida y se detiene
    con un mensaje accionable ante cualquier anomalia.

.PARAMETER Thumbprint
    Huella del certificado de firma, presente en Cert:\CurrentUser\My o
    Cert:\LocalMachine\My.

.EXAMPLE
    .\build-signed-msi.ps1 -Thumbprint "A1B2C3D4E5F6..."
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Thumbprint,

    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$OutputDir = "",
    [switch]$SkipRar
)

$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

$script:Root = $PSScriptRoot
$script:ExePath = Join-Path $script:Root "bin\AgilEx_by_Marduk.exe"
$script:WxsPath = Join-Path $script:Root "wix\Product.wxs"
$script:ManifestPath = Join-Path $script:Root "MANIFIESTO.txt"
$script:IsSelfSigned = $false
$script:SignTool = $null
$script:RarExe = $null

if ($OutputDir -eq "") { $OutputDir = Join-Path $script:Root "salida" }
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

$script:TranscriptPath = Join-Path $OutputDir "transcript.log"
Start-Transcript -Path $script:TranscriptPath -Force | Out-Null

function Write-Stage {
    param([string]$Message)
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Stop-WithError {
    param([string]$Message, [string]$Action, [int]$Code)
    Write-Host ""
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    Write-Host "[ACCION] $Action" -ForegroundColor Yellow
    Stop-Transcript | Out-Null
    exit $Code
}

function Find-SignTool {
    $base = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    if (-not (Test-Path $base)) { return $null }
    $found = Get-ChildItem $base -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\x64\\" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($found) { return $found.FullName }
    return $null
}

function Find-Rar {
    $candidates = @(
        "$env:ProgramFiles\WinRAR\Rar.exe",
        "${env:ProgramFiles(x86)}\WinRAR\Rar.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function Test-Prerequisites {
    Write-Stage "Etapa 0/6 - Preflight"

    $script:SignTool = Find-SignTool
    if (-not $script:SignTool) {
        Stop-WithError -Message "No se encontro signtool.exe" `
            -Action "Instale el Windows SDK (componente Signing Tools)." -Code 10
    }
    Write-Host "[OK] signtool: $($script:SignTool)" -ForegroundColor Green

    $wix = Get-Command wix -ErrorAction SilentlyContinue
    if (-not $wix) {
        Stop-WithError -Message "No se encontro la herramienta wix" `
            -Action "Ejecute: dotnet tool install --global wix" -Code 10
    }
    Write-Host "[OK] wix: $($wix.Source)" -ForegroundColor Green

    $script:RarExe = Find-Rar
    if (-not $script:RarExe -and -not $SkipRar) {
        Write-Host "[AVISO] Rar.exe no encontrado. La etapa 5 se omitira." -ForegroundColor Yellow
    }

    if (-not (Test-Path $script:ExePath)) {
        Stop-WithError -Message "No se encontro bin\AgilEx_by_Marduk.exe" `
            -Action "Verifique que descomprimio el paquete completo." -Code 10
    }

    if (-not (Test-Path $script:ManifestPath)) {
        Stop-WithError -Message "No se encontro MANIFIESTO.txt" `
            -Action "Verifique que descomprimio el paquete completo." -Code 10
    }

    $cert = Get-ChildItem -Path Cert:\CurrentUser\My, Cert:\LocalMachine\My -ErrorAction SilentlyContinue |
        Where-Object { $_.Thumbprint -eq $Thumbprint } |
        Select-Object -First 1

    if (-not $cert) {
        Stop-WithError -Message "No se encontro el certificado $Thumbprint" `
            -Action "Verifique la huella con: Get-ChildItem Cert:\CurrentUser\My" -Code 10
    }

    if ($cert.NotAfter -lt (Get-Date)) {
        Stop-WithError -Message "El certificado vencio el $($cert.NotAfter)" `
            -Action "Use un certificado vigente." -Code 10
    }

    # La extension Extended Key Usage se identifica por su OID 2.5.29.37.
    # No se compara Oid.FriendlyName porque esta localizado por idioma del
    # sistema: en Windows en espanol es "Uso mejorado de claves", no
    # "Enhanced Key Usage", y la comparacion literal fallaria siempre.
    $CODE_SIGNING_OID = "1.3.6.1.5.5.7.3.3"
    $EKU_EXTENSION_OID = "2.5.29.37"

    $hasCodeSigning = $false
    foreach ($ext in $cert.Extensions) {
        if ($ext.Oid.Value -ne $EKU_EXTENSION_OID) { continue }
        if ($ext -is [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]) {
            foreach ($usage in $ext.EnhancedKeyUsages) {
                if ($usage.Value -eq $CODE_SIGNING_OID) { $hasCodeSigning = $true }
            }
        }
        # Respaldo: si el tipo fuerte no esta disponible, buscar el OID en el texto
        if (-not $hasCodeSigning -and $ext.Format($false) -match [regex]::Escape($CODE_SIGNING_OID)) {
            $hasCodeSigning = $true
        }
    }

    if (-not $hasCodeSigning) {
        Stop-WithError -Message "El certificado no tiene EKU Code Signing (OID $CODE_SIGNING_OID)" `
            -Action "Use un certificado emitido para firma de codigo." -Code 10
    }

    $script:IsSelfSigned = ($cert.Subject -eq $cert.Issuer)

    Write-Host "[OK] Certificado: $($cert.Subject)" -ForegroundColor Green
    Write-Host "     Vigencia hasta: $($cert.NotAfter)" -ForegroundColor Gray
    if ($script:IsSelfSigned) {
        Write-Host "[AVISO] Certificado autofirmado: modo de prueba." -ForegroundColor Yellow
    }

    return $cert
}

function Test-BinaryIntegrity {
    Write-Stage "Etapa 1/6 - Verificacion de integridad"

    $declared = (Get-Content $script:ManifestPath |
        Where-Object { $_ -match "^SHA256=" }) -replace "^SHA256=", ""
    $declared = $declared.Trim().ToUpper()

    if (-not $declared) {
        Stop-WithError -Message "MANIFIESTO.txt no declara SHA256" `
            -Action "Solicite al desarrollador un paquete valido." -Code 20
    }

    $actual = (Get-FileHash $script:ExePath -Algorithm SHA256).Hash.ToUpper()

    if ($actual -ne $declared) {
        Stop-WithError -Message "El SHA256 del ejecutable no coincide con el declarado.`n  Esperado: $declared`n  Obtenido: $actual" `
            -Action "NO FIRMAR. El binario fue alterado en transito. Solicite reenvio." -Code 20
    }

    Write-Host "[OK] SHA256 verificado: $actual" -ForegroundColor Green
    return $actual
}

# ----- Bloque principal -----
$cert = Test-Prerequisites
$hashBefore = Test-BinaryIntegrity

Write-Host ""
Write-Host "Etapas 0 y 1 completadas." -ForegroundColor Green
Stop-Transcript | Out-Null
