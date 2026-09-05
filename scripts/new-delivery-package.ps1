<#
.SYNOPSIS
    Genera el paquete de entrega para el area de Seguridad Informatica.

.DESCRIPTION
    Empaqueta el ejecutable sin firmar, los fuentes WiX (incluido el icono),
    el script de firma y el MANIFIESTO.txt con el SHA256 declarado.
#>
param(
    [string]$ExePath = "",
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
if ($ExePath -eq "") { $ExePath = Join-Path $root "dist\AgilEx_by_Marduk.exe" }
if ($OutputDir -eq "") { $OutputDir = Join-Path $root "dist" }

if (-not (Test-Path $ExePath)) {
    Write-Host "[ERROR] No se encontro $ExePath" -ForegroundColor Red
    Write-Host "[ACCION] Compile primero: pyinstaller config\main.spec --clean" -ForegroundColor Yellow
    exit 1
}

# Version leida de version_info.rc (fuente de verdad)
$rcPath = Join-Path $root "src\assets\version_info.rc"
$rcContent = Get-Content $rcPath -Raw
if ($rcContent -notmatch "filevers=\((\d+),\s*(\d+),\s*(\d+),") {
    Write-Host "[ERROR] No se pudo leer la version de version_info.rc" -ForegroundColor Red
    exit 1
}
$version = "$($Matches[1]).$($Matches[2]).$($Matches[3])"
Write-Host "[OK] Version detectada: $version" -ForegroundColor Green

$staging = Join-Path $env:TEMP "agilex_delivery_$version"
if (Test-Path $staging) { Remove-Item -Recurse -Force $staging }
New-Item -ItemType Directory -Force -Path "$staging\bin","$staging\wix" | Out-Null

Copy-Item $ExePath "$staging\bin\AgilEx_by_Marduk.exe"
Copy-Item (Join-Path $root "installer\wix\*") "$staging\wix\"
# El .wxs referencia el icono con una ruta relativa local (law_logo.ico), no
# ..\..\src\assets\: fuera del repositorio de desarrollo esa ruta no existe y
# wix build falla con WIX0103. El icono debe viajar junto al .wxs en el paquete.
Copy-Item (Join-Path $root "src\assets\law_logo.ico") "$staging\wix\law_logo.ico"
Copy-Item (Join-Path $root "installer\build-signed-msi.ps1") $staging
Copy-Item (Join-Path $root "installer\README_SEGURIDAD.md") $staging

$hash = (Get-FileHash "$staging\bin\AgilEx_by_Marduk.exe" -Algorithm SHA256).Hash.ToUpper()
$manifest = @(
    "# MANIFIESTO DE ENTREGA - AgilEx by Marduk",
    "# Generado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "# El script de firma verifica este SHA256 antes de firmar.",
    "SHA256=$hash",
    "VERSION=$version"
)
$manifest | Set-Content "$staging\MANIFIESTO.txt" -Encoding UTF8

$zipPath = Join-Path $OutputDir "AgilEx_v${version}_paquete_firma.zip"
if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
Compress-Archive -Path "$staging\*" -DestinationPath $zipPath

Remove-Item -Recurse -Force $staging

Write-Host ""
Write-Host "[OK] Paquete generado: $zipPath" -ForegroundColor Green
Write-Host "     SHA256 del ejecutable: $hash" -ForegroundColor Gray
Write-Host ""
