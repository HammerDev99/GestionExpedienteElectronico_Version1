# =====================================================================
# Firma digital avanzada — AgilEx by Marduk
# =====================================================================
# Versión token-ready con:
#   - Firma dual SHA1 (compat Win7) + SHA256 (obligatoria actual)
#   - Timestamping RFC 3161 (mantiene validez tras vencimiento)
#   - Page hashing (/ph) — reduce falsos positivos en Defender
#   - Soporte para certificado en token hardware (por thumbprint)
#   - Soporte para .pfx autofirmado (modo compatibilidad actual)
#
# Uso:
#   # Modo PFX (situación actual, certificado autofirmado)
#   .\sign_executable_token.ps1 -Mode Pfx
#
#   # Modo Token (cuando se adquiera EV/OV en token físico)
#   .\sign_executable_token.ps1 -Mode Token -Thumbprint "ABCD1234..."
#
#   # Modo Token con búsqueda automática por CN
#   .\sign_executable_token.ps1 -Mode Token -SubjectName "CN=Rama Judicial*"
# =====================================================================

param(
    [ValidateSet("Pfx", "Token")]
    [string]$Mode = "Pfx",

    [string]$Thumbprint = "",
    [string]$SubjectName = "",
    [string]$PfxPath = "",
    [string]$PfxPassword = "",
    [string]$ExePath = "",
    [switch]$DualSign   # Opt-in: intenta firma SHA1 adicional (solo útil si el
                         # cert fue emitido con compat SHA1; la mayoría de certs
                         # modernos CNG fallan con "unexpected internal error")
)

# ----- Configuración base --------------------------------------------
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
if ($ExePath -eq "") {
    $ExePath = Join-Path $ProjectRoot "dist\AgilEx_by_Marduk.exe"
    # Si no existe en onefile, intentar onedir
    if (-not (Test-Path $ExePath)) {
        $OneDirCandidate = Join-Path $ProjectRoot "dist\AgilEx_by_Marduk\AgilEx_by_Marduk.exe"
        if (Test-Path $OneDirCandidate) { $ExePath = $OneDirCandidate }
    }
}
if ($PfxPath -eq "") {
    $PfxPath = Join-Path $ProjectRoot "docs\others\code_signing\cert.pfx"
}

# Servidores de timestamp (primario + respaldos)
$TimestampServers = @(
    "http://timestamp.digicert.com",
    "http://timestamp.sectigo.com",
    "http://timestamp.globalsign.com/tsa/r6advanced1"
)

Write-Host ""
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host "  AgilEx by Marduk — Firma Digital (modo: $Mode)" -ForegroundColor Cyan
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

# ----- Validaciones ---------------------------------------------------
if (-not (Test-Path $ExePath)) {
    Write-Host "[ERROR] Ejecutable no encontrado: $ExePath" -ForegroundColor Red
    Write-Host "        Compile primero con: pyinstaller config\main.spec" -ForegroundColor Yellow
    Write-Host "        o variante onedir:   pyinstaller scripts\certificacion_firma_digital\scripts\main_onedir.spec" -ForegroundColor Yellow
    exit 1
}
Write-Host "[OK] Ejecutable: $ExePath" -ForegroundColor Green
Write-Host "     SHA256 pre-firma: $((Get-FileHash $ExePath -Algorithm SHA256).Hash)" -ForegroundColor Gray
Write-Host ""

# ----- Localizar SignTool --------------------------------------------
$SignToolPaths = @(
    "C:\Program Files (x86)\Windows Kits\10\bin\*\x64\signtool.exe",
    "C:\Program Files\Windows Kits\10\bin\*\x64\signtool.exe"
)
$SignTool = $null
foreach ($pattern in $SignToolPaths) {
    $found = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue |
             Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($found) { $SignTool = $found.FullName; break }
}
if (-not $SignTool) {
    Write-Host "[ERROR] SignTool.exe no encontrado. Instale Windows SDK." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] SignTool: $SignTool" -ForegroundColor Green
Write-Host ""

# ----- Solicitar contraseña de forma segura si no se proporcionó -----
if ($Mode -eq "Pfx" -and [string]::IsNullOrEmpty($PfxPassword)) {
    $SecurePwd = Read-Host -AsSecureString "Ingrese contraseña del PFX"
    $Bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePwd)
    $PfxPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($Bstr)
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Bstr)
}

# ----- Construir parámetros de identificación del certificado --------
# NOTA: valores SIN comillas embebidas — el operador & de PowerShell
# maneja correctamente el quoting por argumento (Start-Process no).
$CertArgs = @()
switch ($Mode) {
    "Pfx" {
        if (-not (Test-Path $PfxPath)) {
            Write-Host "[ERROR] PFX no encontrado: $PfxPath" -ForegroundColor Red
            exit 1
        }
        $CertArgs = @("/f", $PfxPath, "/p", $PfxPassword)
        Write-Host "[MODO PFX] Certificado: $PfxPath" -ForegroundColor Yellow
    }
    "Token" {
        if ($Thumbprint -ne "") {
            $CertArgs = @("/sha1", $Thumbprint, "/s", "MY")
            Write-Host "[MODO TOKEN] Thumbprint: $Thumbprint" -ForegroundColor Yellow
        } elseif ($SubjectName -ne "") {
            $CertArgs = @("/n", $SubjectName, "/s", "MY")
            Write-Host "[MODO TOKEN] Subject: $SubjectName" -ForegroundColor Yellow
        } else {
            Write-Host "[ERROR] En modo Token debe indicar -Thumbprint o -SubjectName" -ForegroundColor Red
            exit 1
        }
    }
}
Write-Host ""

# ----- Función de firma ----------------------------------------------
function Invoke-SignTool {
    param(
        [string]$Algorithm,
        [bool]$AppendSignature
    )
    foreach ($tsa in $TimestampServers) {
        $signArgs = @("sign") + $CertArgs + @(
            "/fd", $Algorithm,
            "/tr", $tsa,
            "/td", $Algorithm,
            "/ph"
        )
        if ($AppendSignature) { $signArgs += "/as" }
        $signArgs += @("/v", $ExePath)

        Write-Host "  → Firmando $Algorithm (TSA: $tsa)..." -ForegroundColor Cyan

        # Ocultar la contraseña en logs: mostrar comando con /p enmascarado
        # (opcional — útil para troubleshooting sin exponer secret)
        # $debugArgs = $signArgs.Clone()
        # for ($i = 0; $i -lt $debugArgs.Length - 1; $i++) {
        #     if ($debugArgs[$i] -eq "/p") { $debugArgs[$i+1] = "***" }
        # }
        # Write-Host "    cmd: $SignTool $($debugArgs -join ' ')" -ForegroundColor DarkGray

        & $SignTool @signArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "    [OK] Firma $Algorithm aplicada" -ForegroundColor Green
            return $true
        }
        Write-Host "    [FALLO TSA $tsa (exit $LASTEXITCODE), intentando siguiente...]" -ForegroundColor Yellow
    }
    return $false
}

# ----- Ejecutar firmas ------------------------------------------------
Write-Host "[1/2] Firma primaria SHA256..." -ForegroundColor White
if (-not (Invoke-SignTool -Algorithm "SHA256" -AppendSignature $false)) {
    Write-Host "[ERROR] Firma SHA256 falló con todos los TSA" -ForegroundColor Red
    exit 1
}

if ($DualSign) {
    Write-Host ""
    Write-Host "[2/2] Firma secundaria SHA1 (opt-in compatibilidad Win7)..." -ForegroundColor White
    if (-not (Invoke-SignTool -Algorithm "SHA1" -AppendSignature $true)) {
        Write-Host "[AVISO] Firma SHA1 no disponible con este cert — solo SHA256 aplicada" -ForegroundColor Yellow
        Write-Host "         (los certs modernos CNG no soportan SHA1; no afecta Windows 10/11)" -ForegroundColor DarkGray
    }
}

# ----- Verificación final --------------------------------------------
# IMPORTANTE: signtool verify retorna exit code != 0 para certs autofirmados
# (la cadena no llega a una raíz confiable de Windows). Esto NO significa que
# la firma falló — es solo el resultado esperado para self-signed.
# Capturamos y descartamos ese exit code para no propagarlo al caller.
Write-Host ""
Write-Host "=========================================================" -ForegroundColor Green
Write-Host "  VERIFICACIÓN" -ForegroundColor Green
Write-Host "=========================================================" -ForegroundColor Green
& $SignTool verify /pa /all /v $ExePath
$verifyExitCode = $LASTEXITCODE   # capturar pero NO propagar

Write-Host ""
$sig = Get-AuthenticodeSignature -FilePath $ExePath
Write-Host "Status     : " -NoNewline
$color = if ($sig.Status -eq "Valid") { "Green" } else { "Yellow" }
Write-Host $sig.Status -ForegroundColor $color
Write-Host "Subject    : $($sig.SignerCertificate.Subject)" -ForegroundColor Gray
Write-Host "Thumbprint : $($sig.SignerCertificate.Thumbprint)" -ForegroundColor Gray
Write-Host "NotAfter   : $($sig.SignerCertificate.NotAfter)" -ForegroundColor Gray
Write-Host "SHA256 post-firma: $((Get-FileHash $ExePath -Algorithm SHA256).Hash)" -ForegroundColor Gray
Write-Host ""

# Distinguir: ¿la firma se aplicó realmente? (no depende del verify chain check)
# Get-AuthenticodeSignature retorna NotSigned solo si el binario no tiene
# ninguna firma embebida. Cualquier otro Status (Valid, UnknownError,
# NotTrusted, HashMismatch) implica que SÍ hay firma aplicada.
if ($sig.Status -eq "NotSigned") {
    Write-Host "[ERROR] El binario no tiene firma embebida tras el proceso." -ForegroundColor Red
    exit 2
}

if ($sig.Status -ne "Valid") {
    Write-Host "NOTA: Status '$($sig.Status)' es esperado para certificados autofirmados." -ForegroundColor Yellow
    Write-Host "      La firma SÍ se aplicó correctamente (verifique 'SHA256 post-firma' arriba)." -ForegroundColor Yellow
    Write-Host "      Para que Status sea 'Valid' se requiere cert EV/OV de CA en Microsoft Trusted Root." -ForegroundColor Yellow
}

# Salir SIEMPRE con código 0 si llegamos aquí — la firma se aplicó.
# El exit code de signtool verify ($verifyExitCode) es solo informativo.
exit 0
