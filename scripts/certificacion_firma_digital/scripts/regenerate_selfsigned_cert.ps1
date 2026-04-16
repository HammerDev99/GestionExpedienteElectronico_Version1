# =====================================================================
# Regeneración del certificado autofirmado — AgilEx by Marduk
# ---------------------------------------------------------------------
# Corrige los hallazgos documentados en HALLAZGOS_CERT_ACTUAL.md:
#   1. Certificado vigente (3 años, vs 1 año anterior)
#   2. Subject institucional consistente con VERSIONINFO
#   3. EKU explícita de Code Signing (1.3.6.1.5.5.7.3.3)
#   4. PFX protegido con contraseña
#   5. Algoritmo de firma SHA256 (explícito)
#   6. Llave RSA 4096 bits
#
# Uso:
#   .\regenerate_selfsigned_cert.ps1
#     -PfxPassword (ConvertTo-SecureString "MiPassSegura" -AsPlainText -Force)
#
# Salida:
#   docs/others/code_signing/cert.pfx       (nuevo, con password)
#   docs/others/code_signing/cert.pem       (público, para compartir)
#   docs/others/code_signing/cert_public.cer (formato DER para SOC)
# =====================================================================

param(
    [securestring]$PfxPassword,
    [string]$OutputDir = "",
    [int]$YearsValid = 3,
    [switch]$BackupOld
)

$ErrorActionPreference = "Stop"

# Detectar raíz del proyecto buscando marcadores (config/main.spec o .git)
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
    Write-Host "[ERROR] No se pudo detectar la raíz del proyecto desde $PSScriptRoot" -ForegroundColor Red
    exit 1
}
if ($OutputDir -eq "") {
    $OutputDir = Join-Path $ProjectRoot "docs\others\code_signing"
}

# Crear directorio de salida si no existe
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    Write-Host "[OK] Directorio creado: $OutputDir" -ForegroundColor Gray
}

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  Regeneración de Certificado Autofirmado — AgilEx" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

if (-not $PfxPassword) {
    $PfxPassword = Read-Host -AsSecureString "Ingrese contraseña para el nuevo PFX (no dejar vacía)"
    if ($PfxPassword.Length -eq 0) {
        Write-Host "[ERROR] La contraseña no puede estar vacía (es un hallazgo de seguridad)." -ForegroundColor Red
        exit 1
    }
}

# ----- Limpieza de certificados huérfanos previos --------------------
# (intentos fallidos de generación dejan certificados en el almacén sin PFX exportado)
$OrphanCerts = Get-ChildItem Cert:\CurrentUser\My |
    Where-Object { $_.Subject -like "*AgilEx by Marduk*" -or $_.FriendlyName -like "*AgilEx by Marduk*" }

if ($OrphanCerts) {
    Write-Host ""
    Write-Host "[LIMPIEZA] Se encontraron $($OrphanCerts.Count) certificado(s) previo(s) de AgilEx:" -ForegroundColor Yellow
    $OrphanCerts | ForEach-Object {
        Write-Host "   - $($_.Thumbprint)  (vence: $($_.NotAfter))" -ForegroundColor Gray
    }
    $confirm = Read-Host "¿Eliminar estos certificados del almacén antes de generar el nuevo? (s/N)"
    if ($confirm -eq "s" -or $confirm -eq "S") {
        $OrphanCerts | ForEach-Object {
            Remove-Item "Cert:\CurrentUser\My\$($_.Thumbprint)" -Force
            Write-Host "   [removido] $($_.Thumbprint)" -ForegroundColor Gray
        }
    }
    Write-Host ""
}

# Backup del certificado actual si existe
$OldPfx = Join-Path $OutputDir "cert.pfx"
if ((Test-Path $OldPfx) -and $BackupOld) {
    $ts = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupDir = Join-Path $OutputDir "backup_$ts"
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Get-ChildItem $OutputDir -Filter "cert.*" | Copy-Item -Destination $BackupDir
    if (Test-Path (Join-Path $OutputDir "key.pem")) {
        Copy-Item (Join-Path $OutputDir "key.pem") $BackupDir
    }
    Write-Host "[OK] Backup de certificado anterior en: $BackupDir" -ForegroundColor Yellow
    Write-Host ""
}

# ----- Parámetros del nuevo certificado ------------------------------
# NOTA LEGAL: identidad de persona natural (Ley 23/1982 - derechos morales).
# No se usa O= corporativo porque no existe entidad jurídica registrada.
# CN = nombre completo del autor; OU = nombre del proyecto (descriptor).
$Subject = "CN=Daniel Arbelaez Alvarez, OU=AgilEx by Marduk, L=Bogota, S=Bogota D.C., C=CO, E=darbelaal@cendoj.ramajudicial.gov.co"
$NotAfter = (Get-Date).AddYears($YearsValid)

Write-Host "Parámetros del nuevo certificado:" -ForegroundColor White
Write-Host "  Subject     : CN=Daniel Arbelaez Alvarez (persona natural)" -ForegroundColor Gray
Write-Host "                OU=AgilEx by Marduk (proyecto)" -ForegroundColor Gray
Write-Host "                L=Bogota, S=Bogota D.C., C=CO" -ForegroundColor Gray
Write-Host "                E=darbelaal@cendoj.ramajudicial.gov.co" -ForegroundColor Gray
Write-Host "  Vigencia    : $YearsValid años (hasta $($NotAfter.ToString('yyyy-MM-dd')))" -ForegroundColor Gray
Write-Host "  Algoritmo   : RSA 4096 + SHA256" -ForegroundColor Gray
Write-Host "  EKU         : Code Signing (1.3.6.1.5.5.7.3.3)" -ForegroundColor Gray
Write-Host "  Key Usage   : DigitalSignature" -ForegroundColor Gray
Write-Host ""

# ----- Generar certificado -------------------------------------------
Write-Host "[1/4] Generando certificado en almacén CurrentUser\My..." -ForegroundColor Yellow

$cert = New-SelfSignedCertificate `
    -Type CodeSigningCert `
    -Subject $Subject `
    -KeyAlgorithm RSA `
    -KeyLength 4096 `
    -HashAlgorithm SHA256 `
    -KeyUsage DigitalSignature `
    -KeyUsageProperty Sign `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3") `
    -NotAfter $NotAfter `
    -CertStoreLocation "Cert:\CurrentUser\My" `
    -FriendlyName "AgilEx by Marduk Code Signing (self-signed)"

Write-Host "      Thumbprint: $($cert.Thumbprint)" -ForegroundColor Gray
Write-Host ""

# ----- Exportar a PFX (con contraseña) -------------------------------
# NOTA: -CryptoAlgorithmOption TripleDES_SHA1 es obligatorio para
# compatibilidad con signtool 10.x. Si se omite, Windows 11 usa
# AES256-SHA256 por defecto y signtool reporta "password not correct"
# (error engañoso — el password sí es correcto, pero no soporta el
# cifrado PKCS#12 moderno).
Write-Host "[2/4] Exportando PFX con contraseña (TripleDES_SHA1 para compat signtool)..." -ForegroundColor Yellow
$PfxPath = Join-Path $OutputDir "cert.pfx"
Export-PfxCertificate -Cert $cert `
    -FilePath $PfxPath `
    -Password $PfxPassword `
    -CryptoAlgorithmOption TripleDES_SHA1 `
    -Force | Out-Null
Write-Host "      PFX: $PfxPath" -ForegroundColor Gray
Write-Host ""

# ----- Exportar certificado público (.cer DER) ------------------------
Write-Host "[3/4] Exportando certificado público (.cer) para SOC..." -ForegroundColor Yellow
$CerPath = Join-Path $OutputDir "cert_public.cer"
Export-Certificate -Cert $cert -FilePath $CerPath -Type CERT -Force | Out-Null
Write-Host "      CER: $CerPath" -ForegroundColor Gray
Write-Host ""

# ----- Exportar certificado público (.pem) ---------------------------
Write-Host "[4/4] Exportando certificado público (.pem)..." -ForegroundColor Yellow
$PemPath = Join-Path $OutputDir "cert.pem"
$base64 = [System.Convert]::ToBase64String($cert.RawData, [System.Base64FormattingOptions]::InsertLineBreaks)
$pem = "-----BEGIN CERTIFICATE-----`r`n$base64`r`n-----END CERTIFICATE-----"
Set-Content -Path $PemPath -Value $pem -Encoding ASCII
Write-Host "      PEM: $PemPath" -ForegroundColor Gray
Write-Host ""

# ----- Resumen -------------------------------------------------------
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "  CERTIFICADO REGENERADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Thumbprint SHA1  : $($cert.Thumbprint)" -ForegroundColor White
Write-Host "Subject          : $($cert.Subject)" -ForegroundColor Gray
Write-Host "Emitido          : $($cert.NotBefore)" -ForegroundColor Gray
Write-Host "Vence            : $($cert.NotAfter)" -ForegroundColor Gray
Write-Host "EKU              : Code Signing" -ForegroundColor Gray
Write-Host ""
Write-Host "Pasos siguientes:" -ForegroundColor Yellow
Write-Host "  1. Guardar la contraseña del PFX en un gestor de secretos" -ForegroundColor White
Write-Host "  2. Firmar el ejecutable:" -ForegroundColor White
Write-Host "     .\sign_executable_token.ps1 -Mode Pfx -PfxPassword 'LaPass'" -ForegroundColor Cyan
Write-Host "  3. Adjuntar 'cert_public.cer' a la solicitud al SOC" -ForegroundColor White
Write-Host "  4. Actualizar README.md con el nuevo thumbprint" -ForegroundColor White
Write-Host ""
Write-Host "RECORDATORIO: este sigue siendo un certificado autofirmado." -ForegroundColor Yellow
Write-Host "Para eliminar advertencias SmartScreen se requiere EV comercial." -ForegroundColor Yellow
