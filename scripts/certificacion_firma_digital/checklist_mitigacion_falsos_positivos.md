# Checklist — Mitigación de falsos positivos AV/XDR

> Estado de las medidas técnicas de reducción de detecciones heurísticas.
> Complementa (pero **no sustituye**) la adquisición futura de un Code Signing
> comercial de CA en Microsoft Trusted Root Program.

Leyenda: ✅ implementado · ⚠️ parcial · ⬜ pendiente · 🟦 requiere compra

---

## A. Metadatos PE (Portable Executable)

| # | Medida | Estado | Archivo / comando |
|---|---|---|---|
| A1 | `CompanyName` poblado | ✅ | `src/assets/version_info.rc:16` |
| A2 | `ProductName` poblado | ✅ | `src/assets/version_info.rc:23` |
| A3 | `FileDescription` descriptivo | ✅ | `src/assets/version_info.rc:17` |
| A4 | `LegalCopyright` con autor | ✅ | `src/assets/version_info.rc:20` |
| A5 | `OriginalFilename` coincide con `.exe` final | ✅ | `src/assets/version_info.rc:22` |
| A6 | Icono embebido | ✅ | `config/main.spec:109` |
| A7 | Manifiesto UAC `asInvoker` | ✅ | `src/assets/app.manifest:42-45` |

## B. Configuración del bootloader PyInstaller

| # | Medida | Estado | Observación |
|---|---|---|---|
| B1 | UPX desactivado | ✅ | `config/main.spec:103` — UPX dispara FP en ~40% de engines |
| B2 | Build `onefile` como flujo principal | ✅ | `config/main.spec` — único `.exe` evaluado una sola vez por XDR |
| B3 | `console=False` (sin ventana) | ✅ | `config/main.spec:106` |
| B4 | `strip=False` (no strip de símbolos) | ✅ | Strip agresivo también dispara FP |
| B5 | `uac_admin=False` (no pide admin) | ✅ | `config/main.spec:110` |
| B6 | Reducir `hiddenimports` al mínimo real | ⬜ | Auditar módulos realmente usados |
| B7 | Variante `onedir` solo para análisis VT | ✅ | `scripts/main_onedir.spec` — NO usar para distribución (regresión 2026-04-15) |
| B8 | Script todo-en-uno `build_and_sign.ps1` | ✅ | Limpia + compila onefile + firma en un solo comando |

## C. Firma Authenticode

| # | Medida | Estado | Archivo |
|---|---|---|---|
| C0 | **Cert autofirmado vigente** | 🔴 | **VENCIDO 2026-03-04** — usar `scripts/regenerate_selfsigned_cert.ps1` |
| C1 | Firma SHA256 aplicada post-build | ⚠️ | Con cert autofirmado (no confiable) |
| C2 | Timestamp RFC 3161 | ✅ | `sign_executable.ps1:115` (digicert TSA) |
| C3 | Fallback a múltiples TSA | ⬜ | Implementado en nuevo script `sign_executable_token.ps1` |
| C4 | Page hashing (`/ph`) activo | ⬜ | Implementado en nuevo script `sign_executable_token.ps1` |
| C5 | Dual-signing SHA1+SHA256 | ⬜ | Implementado en nuevo script `sign_executable_token.ps1` |
| C6 | EKU Code Signing explícita en cert | 🔴 | Cert actual no la declara — nuevo script sí |
| C7 | Subject institucional consistente con VERSIONINFO | 🔴 | Actual: `O=HammerDev99` / deseado: `O=Consejo Superior de la Judicatura` |
| C8 | PFX protegido con contraseña | 🔴 | Actual: contraseña vacía — nuevo script exige password |
| C9 | Certificado emitido por CA en Microsoft Trusted Root | 🟦 | Requiere compra (SSL.com OV / DigiCert EV) |
| C10 | Certificado EV (reputación SmartScreen inmediata) | 🟦 | Objetivo final para despliegue nacional |

## D. Reputación y reporte

| # | Medida | Estado | Referencia |
|---|---|---|---|
| D1 | Repositorio público y auditable | ✅ | github.com/HammerDev99/GestionExpedienteElectronico_Version1 |
| D2 | Reporte de FP a Microsoft WDSI | ⬜ | `plantillas/reporte_falso_positivo_microsoft.md` |
| D3 | Solicitud whitelist a SOC Rama Judicial | ⬜ | `plantillas/solicitud_whitelist_soc.md` |
| D4 | Whitelist por thumbprint (no por hash) | ⬜ | Requisito crítico — no repetir por versión |
| D5 | Registro de despliegues sin incidentes (reputación orgánica) | ⬜ | Llevar bitácora tras remediación |

## E. Buenas prácticas de build

| # | Medida | Estado |
|---|---|---|
| E1 | Build reproducible (mismo hash con mismos fuentes) | ⬜ Evaluar `PYTHONHASHSEED=0` y timestamp fijo |
| E2 | Pipeline CI con firma automatizada | ⬜ |
| E3 | Publicación con checksums SHA256 visibles | ⬜ Anexar en release GitHub |
| E4 | VirusTotal scan previo a release (detección temprana) | ⬜ |

---

## Orden de ejecución actualizado (post-regresión 2026-04-15)

1. **Regenerar certificado autofirmado** (solo si está vencido o cambian datos del Subject):
   ```powershell
   .\scripts\certificacion_firma_digital\scripts\regenerate_selfsigned_cert.ps1 -BackupOld
   ```
2. **Build + firma en un solo comando** (flujo recomendado, modo onefile):
   ```powershell
   .\scripts\certificacion_firma_digital\scripts\build_and_sign.ps1
   ```
3. **Subir binario firmado a VirusTotal** (URL impresa por el script):
   `https://www.virustotal.com/gui/home/upload`
4. **Probar en equipo de la entidad** (golden path: instalación + ejecución de un expediente).
5. **Radicar correo formal al SOC** con `evidencias/solicitud_whitelist_soc_FINAL.docx`.
6. **Registrar** thumbprint y SHA256 nuevos en la tabla de control del `README.md`.

---

## Criterio de éxito (sin cert comercial aún)

- [x] Build `onefile` firmado pasa VirusTotal con ≤2 detecciones (logrado: 1/72 con onedir; pendiente verificar onefile post-pivote)
- [x] Microsoft Defender en VT no detecta el binario actual
- [ ] SOC Rama Judicial confirma whitelist por thumbprint
- [ ] Re-despliegue en BAQ ejecuta sin cierre automático (criterio principal post-regresión)

## Criterio de éxito (con EV Code Signing)

- [ ] Windows muestra publisher verificado en el primer `run`
- [ ] SmartScreen no interrumpe instalación
- [ ] VirusTotal ≤0–1 detecciones
- [ ] Cero alertas XDR en despliegue nacional
