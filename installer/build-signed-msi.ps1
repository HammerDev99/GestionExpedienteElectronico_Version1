<#
.SYNOPSIS
    Firma y empaqueta AgilEx by Marduk como MSI distribuible.

.DESCRIPTION
    Ejecuta seis etapas: preflight, verificacion de integridad, firma del
    ejecutable, empaquetado MSI, firma del MSI y compresion RAR. Genera
    REPORTE_FIRMA.txt como evidencia.

    El script no toma decisiones ni corrige errores: valida y se detiene
    con un mensaje accionable ante cualquier anomalia.

    Soporta dos modos de firma, excluyentes entre si:

      - Almacen local: el certificado esta instalado en el almacen de
        Windows y se referencia por su huella (-Thumbprint). Aplica a
        certificados en archivo PFX importado o en token fisico/HSM.

      - Azure Key Vault: la llave privada nunca sale del vault; se firma
        de forma remota con AzureSignTool (-KeyVaultUrl y -KeyVaultCertificate).
        Es el modo recomendado cuando la entidad ya opera un Key Vault,
        porque ningun material sensible se transporta ni se instala en la
        estacion de firma.

.PARAMETER Thumbprint
    Modo almacen local. Huella del certificado de firma, presente en
    Cert:\CurrentUser\My o Cert:\LocalMachine\My.

.PARAMETER KeyVaultUrl
    Modo Azure Key Vault. URL del vault, por ejemplo
    https://kv-csj-utdi-prd.vault.azure.net

.PARAMETER KeyVaultCertificate
    Modo Azure Key Vault. Nombre del certificado dentro del vault.

.PARAMETER KeyVaultClientId
    Modo Azure Key Vault. Client ID del service principal. Si se omite,
    AzureSignTool usa la credencial administrada / sesion de Azure CLI.

.PARAMETER KeyVaultClientSecret
    Modo Azure Key Vault. Secret del service principal. Se recomienda
    omitirlo y autenticar con `az login` para no exponerlo en la linea
    de comandos ni en el historial de la consola.

.PARAMETER KeyVaultTenantId
    Modo Azure Key Vault. Tenant ID del directorio de Azure.

.EXAMPLE
    .\build-signed-msi.ps1 -Thumbprint "A1B2C3D4E5F6..."

.EXAMPLE
    az login
    .\build-signed-msi.ps1 -KeyVaultUrl "https://kv-csj-utdi-prd.vault.azure.net" `
        -KeyVaultCertificate "agilex-code-signing"
#>
[CmdletBinding(DefaultParameterSetName = "LocalStore")]
param(
    [Parameter(Mandatory = $true, ParameterSetName = "LocalStore")]
    [string]$Thumbprint,

    [Parameter(Mandatory = $true, ParameterSetName = "KeyVault")]
    [string]$KeyVaultUrl,

    [Parameter(Mandatory = $true, ParameterSetName = "KeyVault")]
    [string]$KeyVaultCertificate,

    [Parameter(ParameterSetName = "KeyVault")]
    [string]$KeyVaultClientId,

    [Parameter(ParameterSetName = "KeyVault")]
    [string]$KeyVaultClientSecret,

    [Parameter(ParameterSetName = "KeyVault")]
    [string]$KeyVaultTenantId,

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
$script:AzureSignTool = $null
$script:RarExe = $null
$script:SignMode = $PSCmdlet.ParameterSetName

# Cierra el transcript de forma tolerante: si nunca se inicio (por ejemplo,
# porque el fallo ocurrio antes de Start-Transcript), Stop-Transcript lanza
# "The host is not currently transcribing", un error crudo de PowerShell que
# no aporta nada al operador y ensucia un mensaje que de otro modo es claro.
function Close-TranscriptSafely {
    try { Stop-Transcript | Out-Null } catch { }
}

# Cierra el transcript ante cualquier excepcion terminante no controlada por
# Stop-WithError (permisos, rutas invalidas, fallos de Get-FileHash, etc.).
# Ninguna ruta de salida debe dejar el transcript abierto: un transcript
# huerfano contamina la evidencia de ejecuciones posteriores en la consola.
trap {
    Write-Host ""
    Write-Host "[ERROR] Error no controlado: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "[ACCION] Revise el detalle del error arriba y contacte al desarrollador." -ForegroundColor Yellow
    Close-TranscriptSafely
    exit 99
}

if ($OutputDir -eq "") { $OutputDir = Join-Path $script:Root "salida" }

# Normaliza a ruta absoluta antes de crear el directorio. Build-Msi hace
# Push-Location hacia installer\wix\ antes de invocar wix build, y un
# OutputDir relativo se resolveria contra ese directorio en vez del
# directorio de invocacion original, dejando el MSI en un sitio distinto
# al que buscan las etapas siguientes. No se usa [IO.Path]::GetFullPath
# porque esa API resuelve contra Environment.CurrentDirectory, que
# Set-Location de PowerShell no sincroniza: produciria el mismo bug con
# otro nombre. $PWD si refleja el directorio real de la sesion.
if (-not [System.IO.Path]::IsPathRooted($OutputDir)) {
    $OutputDir = Join-Path $PWD.Path $OutputDir
}
$OutputDir = [System.IO.Path]::GetFullPath($OutputDir)

if (-not (Test-Path $OutputDir)) {
    try {
        New-Item -ItemType Directory -Force -Path $OutputDir -ErrorAction Stop | Out-Null
    } catch {
        Write-Host ""
        Write-Host "[ERROR] No se pudo crear el directorio de salida: $OutputDir" -ForegroundColor Red
        Write-Host "[ACCION] Verifique que la ruta de -OutputDir existe y es accesible, o use el valor por defecto." -ForegroundColor Yellow
        exit 10
    }
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
    Close-TranscriptSafely
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

function Find-AzureSignTool {
    $cmd = Get-Command AzureSignTool -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    $dotnetTool = Join-Path $env:USERPROFILE ".dotnet\tools\AzureSignTool.exe"
    if (Test-Path $dotnetTool) { return $dotnetTool }
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

    Write-Host "[INFO] Modo de firma: $(if ($script:SignMode -eq 'KeyVault') { 'Azure Key Vault (firma remota)' } else { 'Almacén local de Windows' })" -ForegroundColor Gray

    if ($script:SignMode -eq "KeyVault") {
        $script:AzureSignTool = Find-AzureSignTool
        if (-not $script:AzureSignTool) {
            $astAction = "Instálela con: dotnet tool install --global AzureSignTool`n" `
                + "     Si ya está instalada, agregue %USERPROFILE%\.dotnet\tools al PATH y abra una consola nueva."
            Stop-WithError -Message "No se encontró AzureSignTool" -Action $astAction -Code 10
        }
        Write-Host "[OK] AzureSignTool: $($script:AzureSignTool)" -ForegroundColor Green
    }
    else {
        $script:SignTool = Find-SignTool
        if (-not $script:SignTool) {
            Stop-WithError -Message "No se encontró signtool.exe" `
                -Action "Verifique primero si el Windows SDK esta instalado (revise `"C:\Program Files (x86)\Windows Kits\10\bin`"). Si no esta, instale el componente `"Signing Tools for Desktop Apps`" del Windows SDK." -Code 10
        }
        Write-Host "[OK] signtool: $($script:SignTool)" -ForegroundColor Green
    }

    $wix = Get-Command wix -ErrorAction SilentlyContinue
    if (-not $wix) {
        $wixAction = "Verifique primero si ya esta instalada con: dotnet tool list --global`n" `
            + "     Si aparece en la lista, el problema es el PATH: agregue %USERPROFILE%\.dotnet\tools al PATH del usuario y abra una consola nueva.`n" `
            + "     Si no aparece, instalela con: dotnet tool install --global wix --version 6.0.1"
        Stop-WithError -Message "No se encontró la herramienta wix en el PATH" `
            -Action $wixAction -Code 10
    }
    Write-Host "[OK] wix: $($wix.Source)" -ForegroundColor Green

    $script:RarExe = Find-Rar
    if (-not $script:RarExe -and -not $SkipRar) {
        Write-Host "[AVISO] Rar.exe no encontrado. La etapa 5 se omitirá." -ForegroundColor Yellow
    }

    if (-not (Test-Path $script:ExePath)) {
        Stop-WithError -Message "No se encontró bin\AgilEx_by_Marduk.exe" `
            -Action "Verifique que descomprimió el paquete completo." -Code 10
    }

    if (-not (Test-Path $script:ManifestPath)) {
        Stop-WithError -Message "No se encontró MANIFIESTO.txt" `
            -Action "Verifique que descomprimió el paquete completo." -Code 10
    }

    # En modo Key Vault la llave vive en Azure: no hay certificado local que
    # inspeccionar. AzureSignTool valida el EKU contra el vault al firmar, y
    # la etapa 2 se detiene si el certificado no sirve para firma de codigo.
    if ($script:SignMode -eq "KeyVault") {
        Write-Host "[OK] Vault: $KeyVaultUrl" -ForegroundColor Green
        Write-Host "     Certificado: $KeyVaultCertificate" -ForegroundColor Gray
        if (-not $KeyVaultClientId) {
            Write-Host "[INFO] Sin -KeyVaultClientId: se usará la sesión de Azure CLI o la identidad administrada." -ForegroundColor Gray
        }
        return $null
    }

    $cert = Get-ChildItem -Path Cert:\CurrentUser\My, Cert:\LocalMachine\My -ErrorAction SilentlyContinue |
        Where-Object { $_.Thumbprint -eq $Thumbprint } |
        Select-Object -First 1

    if (-not $cert) {
        Stop-WithError -Message "No se encontró el certificado $Thumbprint" `
            -Action "Verifique la huella con: Get-ChildItem Cert:\CurrentUser\My" -Code 10
    }

    if ($cert.NotAfter -lt (Get-Date)) {
        Stop-WithError -Message "El certificado venció el $($cert.NotAfter)" `
            -Action "Use un certificado vigente." -Code 10
    }

    # La extension Extended Key Usage se identifica por su OID 2.5.29.37.
    # No se compara Oid.FriendlyName porque esta localizado por idioma del
    # sistema: en Windows en espanol es "Uso mejorado de claves", no
    # "Enhanced Key Usage", y la comparacion literal fallaria siempre.
    $CODE_SIGNING_OID = "1.3.6.1.5.5.7.3.3"
    $EKU_EXTENSION_OID = "2.5.29.37"
    $SERVER_AUTH_OID = "1.3.6.1.5.5.7.3.1"

    $hasCodeSigning = $false
    $foundEkus = @()
    foreach ($ext in $cert.Extensions) {
        if ($ext.Oid.Value -ne $EKU_EXTENSION_OID) { continue }
        if ($ext -is [System.Security.Cryptography.X509Certificates.X509EnhancedKeyUsageExtension]) {
            foreach ($usage in $ext.EnhancedKeyUsages) {
                $foundEkus += $usage.Value
                if ($usage.Value -eq $CODE_SIGNING_OID) { $hasCodeSigning = $true }
            }
        }
        # Respaldo: si el tipo fuerte no esta disponible, buscar el OID en el texto
        if (-not $hasCodeSigning -and $ext.Format($false) -match [regex]::Escape($CODE_SIGNING_OID)) {
            $hasCodeSigning = $true
        }
    }

    if (-not $hasCodeSigning) {
        # Diagnostico explicito: el error mas probable en una entidad es que
        # entreguen el certificado TLS del dominio institucional, que es el
        # que administran a diario, en vez de uno de firma de codigo. Nombrar
        # esa confusion ahorra un ciclo completo de ida y vuelta.
        $ekuDetail = if ($foundEkus) { $foundEkus -join ", " } else { "(el certificado no declara ningún EKU)" }
        $msg = "El certificado no sirve para firma de código.`n" `
            + "  Subject : $($cert.Subject)`n" `
            + "  EKU presentes: $ekuDetail`n" `
            + "  EKU requerido: $CODE_SIGNING_OID (Code Signing)"

        $action = if ($foundEkus -contains $SERVER_AUTH_OID) {
            "Este es un certificado TLS de servidor web, no de firma de código. Son emisiones distintas:`n" `
                + "     aunque signtool puede forzar la firma con /u, Windows la reporta como no válida para el uso`n" `
                + "     solicitado, y Control de aplicaciones puede bloquear el ejecutable firmado.`n" `
                + "     Solicite al área emisora un certificado con EKU Code Signing (validación OV o EV)."
        } else {
            "Use un certificado emitido para firma de código (EKU $CODE_SIGNING_OID, validación OV o EV)."
        }

        Stop-WithError -Message $msg -Action $action -Code 10
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
    Write-Stage "Etapa 1/6 - Verificación de integridad"

    $declared = (Get-Content $script:ManifestPath |
        Where-Object { $_ -match "^SHA256=" }) -replace "^SHA256=", ""
    $declared = $declared.Trim().ToUpper()

    if (-not $declared) {
        Stop-WithError -Message "MANIFIESTO.txt no declara SHA256" `
            -Action "Solicite al desarrollador un paquete válido." -Code 20
    }

    $actual = (Get-FileHash $script:ExePath -Algorithm SHA256).Hash.ToUpper()

    if ($actual -ne $declared) {
        Stop-WithError -Message "El SHA256 del ejecutable no coincide con el declarado.`n  Esperado: $declared`n  Obtenido: $actual" `
            -Action "NO FIRMAR. El binario fue alterado en tránsito. Solicite reenvío." -Code 20
    }

    Write-Host "[OK] SHA256 verificado: $actual" -ForegroundColor Green
    return $actual
}

function Invoke-SignFile {
    param(
        [string]$Path,
        [string]$Description,
        [int]$ErrorCode
    )

    if ($script:SignMode -eq "KeyVault") {
        $args = @(
            "sign",
            "--azure-key-vault-url", $KeyVaultUrl,
            "--azure-key-vault-certificate", $KeyVaultCertificate,
            "--file-digest", "sha256",
            "--timestamp-rfc3161", $TimestampUrl,
            "--timestamp-digest", "sha256",
            "--description", "AgilEx by Marduk"
        )
        if ($KeyVaultClientId)     { $args += @("--azure-key-vault-client-id", $KeyVaultClientId) }
        if ($KeyVaultClientSecret) { $args += @("--azure-key-vault-client-secret", $KeyVaultClientSecret) }
        if ($KeyVaultTenantId)     { $args += @("--azure-key-vault-tenant-id", $KeyVaultTenantId) }
        if (-not $KeyVaultClientId) { $args += "--azure-key-vault-managed-identity" }
        $args += $Path

        & $script:AzureSignTool @args
        if ($LASTEXITCODE -ne 0) {
            $kvAction = "Verifique:`n" `
                + "     - Que la sesión de Azure esté activa (az login) o que las credenciales del service principal sean correctas.`n" `
                + "     - Que la identidad tenga permisos Get sobre certificados y Sign sobre llaves en el vault.`n" `
                + "     - Que el certificado '$KeyVaultCertificate' exista en el vault y tenga EKU Code Signing (1.3.6.1.5.5.7.3.3).`n" `
                + "     - La conectividad con $TimestampUrl."
            Stop-WithError -Message "AzureSignTool falló al firmar $Description (exit $LASTEXITCODE)" `
                -Action $kvAction -Code $ErrorCode
        }
    }
    else {
        $args = @(
            "sign",
            "/sha1", $Thumbprint,
            "/fd", "SHA256",
            "/td", "SHA256",
            "/tr", $TimestampUrl,
            "/d", "AgilEx by Marduk",
            $Path
        )

        & $script:SignTool @args
        if ($LASTEXITCODE -ne 0) {
            Stop-WithError -Message "signtool falló al firmar $Description (exit $LASTEXITCODE)" `
                -Action "Verifique la conectividad con $TimestampUrl y los permisos del certificado." -Code $ErrorCode
        }
    }

    $sig = Get-AuthenticodeSignature $Path

    if ($sig.Status -eq "Valid") {
        Write-Host "[OK] Firma válida en $Description" -ForegroundColor Green
    }
    elseif ($sig.Status -eq "UnknownError" -and $script:IsSelfSigned) {
        Write-Host "[AVISO] Firma íntegra pero la cadena no encadena a una raíz de confianza." -ForegroundColor Yellow
        Write-Host "        Esperado con certificado autofirmado (modo de prueba)." -ForegroundColor Yellow
    }
    else {
        Stop-WithError -Message "Estado de firma inesperado en ${Description}: $($sig.Status)" `
            -Action "Revise el certificado y vuelva a intentarlo." -Code $ErrorCode
    }

    return $sig
}

function Get-ProductVersion {
    $declared = (Get-Content $script:ManifestPath |
        Where-Object { $_ -match "^VERSION=" }) -replace "^VERSION=", ""
    $declared = $declared.Trim()
    if (-not $declared) {
        Stop-WithError -Message "MANIFIESTO.txt no declara VERSION" `
            -Action "Solicite al desarrollador un paquete válido." -Code 40
    }
    return $declared
}

function Build-Msi {
    param([string]$Version, [string]$Destination)

    Write-Stage "Etapa 3/6 - Empaquetado MSI"

    & wix extension add -g WixToolset.UI.wixext/6.0.1 2>&1 | Out-Null
    & wix extension add -g WixToolset.Util.wixext/6.0.1 2>&1 | Out-Null

    # wix resuelve SourceFile relativo al directorio actual, no al .wxs.
    # Product.wxs referencia el icono como law_logo.ico (ruta relativa local,
    # el icono viaja junto al .wxs en el paquete de entrega), asi que wix
    # debe ejecutarse posicionado en el mismo directorio del .wxs.
    $wxsDir = Split-Path -Parent $script:WxsPath
    Push-Location $wxsDir
    try {
        & wix build (Split-Path -Leaf $script:WxsPath) `
            -arch x64 `
            -ext WixToolset.UI.wixext/6.0.1 `
            -ext WixToolset.Util.wixext/6.0.1 `
            -d ExeSourcePath="$script:ExePath" `
            -d ProductVersion="$Version" `
            -o $Destination
        $exitCode = $LASTEXITCODE
    }
    finally {
        Pop-Location
    }

    if ($exitCode -ne 0) {
        Stop-WithError -Message "wix build falló (exit $exitCode)" `
            -Action "Revise el transcript en $script:TranscriptPath" -Code 40
    }

    Write-Host "[OK] MSI generado: $Destination" -ForegroundColor Green
}

function Compress-Package {
    param([string]$MsiPath, [string]$RarPath)

    Write-Stage "Etapa 5/6 - Compresión RAR"

    if ($SkipRar) {
        Write-Host "[OMITIDO] -SkipRar activo" -ForegroundColor Yellow
        return $false
    }
    if (-not $script:RarExe) {
        Write-Host "[OMITIDO] Rar.exe no disponible. El MSI firmado queda en $MsiPath" -ForegroundColor Yellow
        return $false
    }

    & $script:RarExe a -m5 -ep1 $RarPath $MsiPath | Out-Null

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $RarPath)) {
        Write-Host "[AVISO] La compresión falló. El MSI firmado sigue siendo válido." -ForegroundColor Yellow
        return $false
    }

    Write-Host "[OK] RAR generado: $RarPath" -ForegroundColor Green
    return $true
}

function Write-SignatureReport {
    param(
        [string]$ReportPath,
        $Certificate,
        [string]$Version,
        [string]$ExeHashBefore,
        [string]$ExeHashAfter,
        [string]$MsiPath,
        [string]$MsiHash,
        [bool]$RarCreated
    )

    $exeSig = Get-AuthenticodeSignature $script:ExePath
    $msiSig = Get-AuthenticodeSignature $MsiPath

    # En modo Key Vault no hay objeto de certificado local: los datos del
    # firmante se leen del certificado embebido en la firma resultante.
    $signer = $Certificate
    if (-not $signer) { $signer = $msiSig.SignerCertificate }

    $certLines = if ($signer) {
        @(
            "Subject    : $($signer.Subject)",
            "Issuer     : $($signer.Issuer)",
            "Thumbprint : $($signer.Thumbprint)",
            "Vigencia   : $($signer.NotBefore) a $($signer.NotAfter)"
        )
    } else {
        @("Subject    : (no se pudo leer el certificado de la firma)")
    }

    $originLines = if ($script:SignMode -eq "KeyVault") {
        @(
            "Origen     : Azure Key Vault (firma remota, la llave privada no salió del vault)",
            "Vault      : $KeyVaultUrl",
            "Certificado: $KeyVaultCertificate"
        )
    } else {
        @(
            "Origen     : Almacén local de Windows",
            "Autofirmado: $($script:IsSelfSigned)"
        )
    }

    $lines = @(
        "REPORTE DE FIRMA - AgilEx by Marduk",
        "===================================",
        "",
        "Fecha de ejecución : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "Equipo             : $env:COMPUTERNAME",
        "Versión del producto: $Version",
        "",
        "CERTIFICADO",
        "-----------"
    ) + $certLines + $originLines + @(
        "Timestamp  : $TimestampUrl",
        "",
        "EJECUTABLE",
        "----------",
        "SHA256 antes de firmar : $ExeHashBefore",
        "SHA256 después de firmar: $ExeHashAfter",
        "Estado de firma        : $($exeSig.Status)",
        "",
        "INSTALADOR MSI",
        "--------------",
        "Archivo         : $(Split-Path $MsiPath -Leaf)",
        "SHA256          : $MsiHash",
        "Estado de firma : $($msiSig.Status)",
        "",
        "DISTRIBUCIÓN",
        "------------",
        "RAR generado : $RarCreated",
        "",
        "NOTA SOBRE TRAZABILIDAD",
        "-----------------------",
        "El SHA256 del ejecutable cambia al firmarlo. Si se compara contra",
        "el hash documentado ante el SOC para el binario sin firma",
        "institucional, la diferencia es esperada y no indica alteración.",
        "Incidente relacionado: RJ-MDE-MAL-ALERT-002 / ID 804977."
    )

    $lines | Set-Content -Path $ReportPath -Encoding UTF8
    Write-Host "[OK] Reporte generado: $ReportPath" -ForegroundColor Green
}

# ----- Bloque principal -----
$cert = Test-Prerequisites
$hashBefore = Test-BinaryIntegrity

Write-Stage "Etapa 2/6 - Firma del ejecutable"
Invoke-SignFile -Path $script:ExePath -Description "el ejecutable" -ErrorCode 30 | Out-Null
$hashAfter = (Get-FileHash $script:ExePath -Algorithm SHA256).Hash.ToUpper()

$version = Get-ProductVersion
$msiName = "AgilEx_by_Marduk_v${version}_firmado.msi"
$msiPath = Join-Path $OutputDir $msiName
Build-Msi -Version $version -Destination $msiPath

Write-Stage "Etapa 4/6 - Firma del MSI"
Invoke-SignFile -Path $msiPath -Description "el MSI" -ErrorCode 50 | Out-Null
$msiHash = (Get-FileHash $msiPath -Algorithm SHA256).Hash.ToUpper()

$rarPath = Join-Path $OutputDir "AgilEx_v${version}_firmado.rar"
$rarCreated = Compress-Package -MsiPath $msiPath -RarPath $rarPath

Write-Stage "Etapa 6/6 - Reporte de evidencia"
$reportPath = Join-Path $OutputDir "REPORTE_FIRMA.txt"
Write-SignatureReport -ReportPath $reportPath -Certificate $cert -Version $version `
    -ExeHashBefore $hashBefore -ExeHashAfter $hashAfter `
    -MsiPath $msiPath -MsiHash $msiHash -RarCreated $rarCreated

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host " Proceso completado" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host " Salida: $OutputDir" -ForegroundColor Gray
Write-Host ""

Close-TranscriptSafely
exit 0
