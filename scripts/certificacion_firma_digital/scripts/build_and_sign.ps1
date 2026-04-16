# =====================================================================
# Build + Sign todo-en-uno — AgilEx by Marduk
# ---------------------------------------------------------------------
# Compila el ejecutable en modo ONEFILE (single-file) y lo firma con
# Authenticode SHA256 + timestamp RFC 3161 usando el certificado
# autofirmado actual desde el almacén Cert:\CurrentUser\My.
#
# Por qué ONEFILE: en entornos corporativos con XDR + ASR + AppLocker
# (como Rama Judicial), onedir genera más bloqueos porque expone decenas
# de DLLs sin firma a evaluación individual. Onefile presenta un único
# binario firmado, evaluado una sola vez.
#
# Uso típico:
#   .\scripts\certificacion_firma_digital\scripts\build_and_sign.ps1
#
# Parámetros opcionales:
#   -Thumbprint "ABCD..."  Cert específico (default: cert AgilEx en el almacén)
#   -SkipBuild             Solo firma (asume dist\AgilEx_by_Marduk.exe ya existe)
#   -SkipSign              Solo compila (no firma)
#   -SkipVirusTotal        No genera el bloque informativo de URL VirusTotal
#   -KeepBuildDir          No borra el directorio build/ al final
# =====================================================================

param(
    [string]$Thumbprint = "",
    [string]$SpecPath = "",
    [switch]$SkipBuild,
    [switch]$SkipSign,
    [switch]$SkipVirusTotal,
    [switch]$KeepBuildDir
)

$ErrorActionPreference = "Stop"
$swStart = Get-Date

# ----- Detectar raíz del proyecto -----------------------------------
function Find-ProjectRoot {
    param([string]$StartPath)
    $current = $StartPath
    while ($current -and (Test-Path $current)) {
        if ((Test-Path (Join-Path $current "config\main.spec")) -or
            (Test-Path (Join-Path $current ".git"))) {
            return $current
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { return $null }
        $current = $parent
    }
    return $null
}

$ProjectRoot = Find-ProjectRoot -StartPath $PSScriptRoot
if (-not $ProjectRoot) {
    Write-Host "[ERROR] No se pudo detectar la raíz del proyecto" -ForegroundColor Red
    exit 1
}
Set-Location $ProjectRoot

if ($SpecPath -eq "") { $SpecPath = "config\main.spec" }
$SignScript = Join-Path $PSScriptRoot "sign_executable_token.ps1"
$ExePath = Join-Path $ProjectRoot "dist\AgilEx_by_Marduk.exe"

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  AgilEx by Marduk — Build (onefile) + Sign automatizado" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Project root : $ProjectRoot" -ForegroundColor Gray
Write-Host "Spec         : $SpecPath" -ForegroundColor Gray
Write-Host ""

# ----- Localizar el certificado activo si no se especificó ----------
if (-not $SkipSign) {
    if ($Thumbprint -eq "") {
        $cert = Get-ChildItem Cert:\CurrentUser\My |
            Where-Object { $_.Subject -like "*AgilEx by Marduk*" -or $_.FriendlyName -like "*AgilEx*" } |
            Sort-Object NotAfter -Descending | Select-Object -First 1
        if (-not $cert) {
            Write-Host "[ERROR] No se encontró cert AgilEx en Cert:\CurrentUser\My" -ForegroundColor Red
            Write-Host "        Genere uno primero: .\scripts\certificacion_firma_digital\scripts\regenerate_selfsigned_cert.ps1" -ForegroundColor Yellow
            exit 1
        }
        $Thumbprint = $cert.Thumbprint
        Write-Host "[OK] Cert detectado automáticamente:" -ForegroundColor Green
        Write-Host "     Subject:    $($cert.Subject)" -ForegroundColor Gray
        Write-Host "     Thumbprint: $Thumbprint" -ForegroundColor Gray
        Write-Host "     Vence:      $($cert.NotAfter)" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "[OK] Cert thumbprint indicado: $Thumbprint" -ForegroundColor Green
        Write-Host ""
    }
}

# ----- [1/3] Limpieza ------------------------------------------------
if (-not $SkipBuild) {
    Write-Host "[1/3] Limpiando dist/ y build/ previos..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "dist", "build" -ErrorAction SilentlyContinue
    Write-Host "      [OK] Limpieza completada" -ForegroundColor Gray
    Write-Host ""

    # ----- [2/3] Compilar onefile ------------------------------------
    Write-Host "[2/3] Compilando con PyInstaller (modo onefile)..." -ForegroundColor Yellow
    Write-Host "      pyinstaller $SpecPath --clean" -ForegroundColor DarkGray
    Write-Host ""

    $pyiStart = Get-Date
    & pyinstaller $SpecPath --clean
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERROR] PyInstaller falló (exit $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
    $pyiSecs = [int]((Get-Date) - $pyiStart).TotalSeconds
    Write-Host ""
    Write-Host "      [OK] Build onefile completado en ${pyiSecs}s" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host "[1-2/3] SkipBuild activo — usando ejecutable existente" -ForegroundColor DarkYellow
    Write-Host ""
}

if (-not (Test-Path $ExePath)) {
    Write-Host "[ERROR] No se encontró $ExePath tras el build" -ForegroundColor Red
    exit 1
}

$preHash = (Get-FileHash $ExePath -Algorithm SHA256).Hash
$sizeMB = [math]::Round((Get-Item $ExePath).Length / 1MB, 2)
Write-Host "       Ejecutable:    $ExePath" -ForegroundColor Gray
Write-Host "       Tamaño:        ${sizeMB} MB" -ForegroundColor Gray
Write-Host "       SHA256 antes:  $preHash" -ForegroundColor Gray
Write-Host ""

# ----- [3/3] Firma --------------------------------------------------
if (-not $SkipSign) {
    Write-Host "[3/3] Firmando con Authenticode SHA256 + timestamp..." -ForegroundColor Yellow
    & $SignScript -Mode Token -Thumbprint $Thumbprint
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Firma falló" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} else {
    Write-Host "[3/3] SkipSign activo — ejecutable sin firmar" -ForegroundColor DarkYellow
}

# ----- Resultado y evidencias ---------------------------------------
$postHash = (Get-FileHash $ExePath -Algorithm SHA256).Hash
$EvidDir = Join-Path $ProjectRoot "scripts\certificacion_firma_digital\evidencias"
$HashFile = Join-Path $EvidDir "hash_sha256.txt"
"$postHash  AgilEx_by_Marduk.exe  ($(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))" |
    Out-File -FilePath $HashFile -Encoding UTF8
Write-Host ""
Write-Host "[OK] Hash SHA256 guardado en evidencias: $HashFile" -ForegroundColor Gray

# Limpieza opcional del directorio build/
if (-not $KeepBuildDir -and (Test-Path "build")) {
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Write-Host "[OK] Directorio build/ eliminado (use -KeepBuildDir para conservarlo)" -ForegroundColor Gray
}

$totalSecs = [int]((Get-Date) - $swStart).TotalSeconds
Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "  PROCESO COMPLETADO en ${totalSecs}s" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ejecutable firmado : $ExePath" -ForegroundColor White
Write-Host "Tamaño             : ${sizeMB} MB" -ForegroundColor Gray
Write-Host "SHA256 final       : $postHash" -ForegroundColor Gray
Write-Host "Cert thumbprint    : $Thumbprint" -ForegroundColor Gray
Write-Host ""

if (-not $SkipVirusTotal) {
    Write-Host "Validar en VirusTotal (subir manualmente):" -ForegroundColor Cyan
    Write-Host "  https://www.virustotal.com/gui/home/upload" -ForegroundColor Cyan
    Write-Host "Después consultar resultado en:" -ForegroundColor Cyan
    Write-Host "  https://www.virustotal.com/gui/file/$($postHash.ToLower())" -ForegroundColor Cyan
    Write-Host ""
}

Write-Host "Distribución (usuario final solo necesita este archivo):" -ForegroundColor White
Write-Host "  $ExePath" -ForegroundColor Gray
Write-Host ""
