# Certificación y Firma Digital — AgilEx by Marduk

> Carpeta de control de la gestión de certificación y mitigación de falsos positivos
> antivirus/XDR para despliegue en entidades del Estado colombiano (Rama Judicial).
>
> **Incidente disparador:** `RJ-MDE-MAL-ALERT-002` / ID `804977` — Microsoft XDR marcó
> `AgilEx_by_Marduk.exe` como `Malgent` en un equipo de la Rama Judicial
> (abril 2026). Causal declarada por el SOC: *"comportamiento, firma digital o reputación"*.

---

## 1. Recomendación de reputación máxima (software nacional — entidad del Estado)

Para un software de uso nacional desplegado en una entidad del Estado, la opción con
**mayor reputación, seguridad y menor fricción operativa** es:

### 🥇 Primera opción — **EV Code Signing de DigiCert**

| Criterio | Razón |
|---|---|
| Reputación Microsoft SmartScreen | **Inmediata** desde la primera firma, sin período de calentamiento |
| Raíz en Microsoft Trusted Root Program | Sí, desde hace >20 años |
| Validación de identidad | Extendida (EV): verificación jurídica presencial |
| Hardware FIPS 140-2 | Token físico obligatorio — cumple requisitos CA/B Forum 2023 |
| Percepción institucional | CA referente mundial usada por gobiernos, banca, salud |
| Costo | USD 500–700/año |

### 🥈 Segunda opción — **EV Code Signing de GlobalSign o Sectigo**

Equivalentes técnicamente. DigiCert gana por percepción de marca en auditorías.

### ⚠️ Por qué **no** sirven las opciones nacionales

| Proveedor | Acreditación ONAC | En Microsoft Trusted Root | Resuelve XDR |
|---|---|---|---|
| Certicámara (Firma Digital Persona Natural) | ✅ | ❌ | ❌ |
| Andes SCD (Firma de Código) | ✅ | ❌ | ❌ |
| Camerfirma Colombia | ✅ | ❌ (raíz distrusted por Mozilla/Microsoft en 2021) | ❌ |

> Las ECD colombianas acreditadas por ONAC son válidas para firma de **documentos**
> bajo Ley 527/1999. No sirven para firmar ejecutables Windows (Authenticode).

---

## 2. Plan en tres fases

### Fase 0 — Mitigación inmediata sin costo (ESTA GESTIÓN)

Todo lo contenido en esta carpeta. Objetivo: reducir la probabilidad de falso positivo
**sin adquirir aún un certificado comercial**, mientras se gestiona el presupuesto.

- [x] Metadatos VERSIONINFO completos (consistentes con cert: `Daniel Arbelaez Alvarez`)
- [x] Manifiesto UAC `asInvoker` (ya presente en `src/assets/app.manifest`)
- [x] UPX desactivado (ya en `config/main.spec:103`)
- [x] Cert autofirmado vigente con identidad persona natural — ver `HALLAZGOS_CERT_ACTUAL.md`
- [x] Build **`onefile`** firmado con SHA256 + timestamp DigiCert — usar `scripts/build_and_sign.ps1`
- [x] Análisis VirusTotal — 1/72 detecciones, Microsoft Defender no detecta — `evidencias/virustotal_result.txt`
- [ ] Solicitud formal de whitelist al SOC Rama Judicial — `evidencias/solicitud_whitelist_soc_FINAL.docx`
- [ ] Validación cotización Andes SCD EV (preguntas técnicas) — `evidencias/preguntas_andes_scd.md`

> ⚠️ **Regresión 2026-04-15:** la migración a `onedir` que se intentó inicialmente
> empeoró el bloqueo en endpoints corporativos (XDR + ASR + AppLocker terminan el
> proceso al cargar DLLs no firmadas). Decisión: volver a `onefile` como flujo
> principal de distribución. Detalle en `HALLAZGOS_CERT_ACTUAL.md` (Hallazgo 5).

> ⚠️ **Hallazgo crítico descubierto durante el análisis:** el certificado autofirmado
> actual en `docs/others/code_signing/cert.pfx` **venció el 2026-03-04** (hace 42 días
> a la fecha de esta gestión). La detección XDR del 2026-04-06 ocurrió justamente
> después del vencimiento. Detalle completo en `HALLAZGOS_CERT_ACTUAL.md`.

### Fase 1 — Certificado OV de entrada (opcional, presupuesto bajo)

Si no se consigue presupuesto para EV inmediatamente, un **OV de SSL.com (~USD 129/año)**
o **Certum Open Source (~USD 30/año si aplica)** permite que `signtool` produzca una
firma que Windows reconoce como confiable. Requiere tiempo de reputación en SmartScreen
(~semanas–meses según volumen de despliegue).

### Fase 2 — Certificado EV definitivo

DigiCert / GlobalSign EV con token físico. El script `sign_executable_token.ps1` ya
queda listo para recibirlo (firma por thumbprint, sin `.pfx`).

---

## 3. Contenido de esta carpeta

```
scripts/certificacion_firma_digital/
├── README.md                                       ← este archivo
├── HALLAZGOS_CERT_ACTUAL.md                        ← análisis del cert + lección onedir vs onefile
├── RUNBOOK_COMANDOS.md                             ← comandos paso a paso para build + firma
├── checklist_mitigacion_falsos_positivos.md        ← estado actual vs deseado
├── scripts/
│   ├── build_and_sign.ps1                          ← ⭐ TODO-EN-UNO: clean + onefile + firma
│   ├── regenerate_selfsigned_cert.ps1              ← regenera cert con EKU correcta
│   ├── sign_executable_token.ps1                   ← firma con thumbprint del almacén
│   └── main_onedir.spec                            ← variante onedir (solo análisis VT)
├── plantillas/
│   ├── reporte_falso_positivo_microsoft.md         ← plantilla genérica WDSI
│   ├── reporte_wdsi_FINAL.md                       ← reporte FP a Microsoft con datos reales
│   ├── solicitud_whitelist_soc.md                  ← plantilla genérica SOC
│   ├── solicitud_soc_FINAL.md                      ← carta SOC en markdown con datos reales
│   ├── solicitud_whitelist_soc_FINAL.docx          ← ⭐ carta formal Word lista para enviar
│   ├── cuerpo_correo_soc.md                        ← ⭐ cuerpo del correo en markdown
│   └── preguntas_andes_scd.md                      ← validación cotización CA local
└── evidencias/
    ├── cert_public.cer                             ← certificado público para SOC (DER)
    ├── cert_public.rar                             ← certificado comprimido para correo
    ├── hash_sha256.txt                             ← SHA256 del .exe firmado actual
    ├── problemas_firma_equipo_entidad/             ← capturas WhatsApp del incidente XDR
    └── virustotal/
        ├── VirusTotal - File - ...html             ← reporte HTML de VT del binario
        └── virustotal_result.txt                   ← resumen estructurado del análisis
```

---

## 4. Control de versiones de la gestión

| Fecha | Acción | Responsable | Evidencia |
|---|---|---|---|
| 2026-04-06 | Detección Microsoft XDR en endpoint de la Rama Judicial (incidente interno) | SOC Rama Judicial | `../problemas_firma_equipo_entidad/*.jpeg` |
| 2026-04-15 | Apertura de gestión y creación de esta carpeta | Daniel Arbeláez | `README.md` |
| 2026-04-15 | Regeneración cert autofirmado (thumbprint `EDE170B6…D0D7CE2`, vigencia 2029-04-15, EKU Code Signing, Subject institucional) | Daniel Arbeláez | `docs/others/code_signing/backup_20260415_141744/` (cert anterior); nuevo `cert.pfx` / `cert.pem` / `cert_public.cer` |
| 2026-04-15 | Re-regeneración con `TripleDES_SHA1` (thumbprint `FAE8C5A6…9575261`) tras detectar incompatibilidad de signtool con AES256-SHA256 default de Windows 11 | Daniel Arbeláez | `Get-PfxData` confirmó PFX válido; signtool requería cifrado legado. Script `regenerate_selfsigned_cert.ps1` ajustado para este algoritmo |
| _pendiente_ | Rebuild `onedir` + firma dual | — | hash SHA256 antes/después |
| 2026-04-15 | Rebuild `onedir` + firma SHA256 con timestamp DigiCert (thumbprint `FAE8C5A6…9575261`, identidad SprintJudicial) | Daniel Arbeláez | SHA256 post-firma: `78223843EEB28B9477A1284F9E61D8092389F2637F912D958A0E665BFD72DA11` |
| 2026-04-15 | Ajuste legal a persona natural (SprintJudicial sin marca registrada): regeneración cert con `CN=Daniel Arbelaez Alvarez, OU=AgilEx by Marduk` (thumbprint `92ADA07A…0AE7D57B1`, vigencia 2029-04-15). Actualización `version_info.rc`, `app.manifest` y plantilla SOC para reflejar aporte voluntario + derechos morales Ley 23/1982 art. 30 + licencia MIT | Daniel Arbeláez | SHA256 post-firma: `CD89FD0F10C6027221F56C867BF2922DDFE691A6C802A1B383D335FBD1437023`. Evidencias: `evidencias/hash_sha256.txt`, `evidencias/cert_public.cer`. ZIP distribución: `dist/AgilEx_by_Marduk_v1.5.0_signed.zip` |
| 2026-04-15 | Análisis VirusTotal del build onedir firmado: 1/72 detecciones (solo Bkav Pro genérico ML), Microsoft Defender Undetected. Evidencia clave para carta SOC | Daniel Arbeláez | `evidencias/virustotal_result.txt` |
| 2026-04-15 | Generación carta formal SOC (.docx) y cuerpo de correo (.md) con identidad persona natural y datos cert actualizados | Claude | `evidencias/solicitud_whitelist_soc_FINAL.docx`, `evidencias/cuerpo_correo_soc.md` |
| 2026-04-15 | **REGRESIÓN detectada en despliegue:** binario onedir firmado se cierra automáticamente en equipo de Rama Judicial (XDR + ASR + AppLocker bloquean DLLs no firmadas adyacentes). Pivote: regreso a `onefile` como flujo principal de distribución | Daniel Arbeláez | Hallazgo 5 en `HALLAZGOS_CERT_ACTUAL.md` |
| 2026-04-15 | Cotización EV Code Signing recibida de proveedor local. Pendiente validar si raíz está en Microsoft Trusted Root Program antes de comprar | Daniel Arbeláez | `evidencias/preguntas_andes_scd.md` |
| 2026-04-15 | Implementación pivote onefile: limpieza `config/main.spec`, creación `build_and_sign.ps1` (todo-en-uno), actualización RUNBOOK con flujo onefile como principal | Claude | `scripts/build_and_sign.ps1`, `RUNBOOK_COMANDOS.md` |
| 2026-04-15 | Validación cruzada informe Diana: 23 datos técnicos verificados (21 OK, 2 corregidos: tildes en Subject del cert + manifest version 1.4.4→1.5.0). Recompilación + re-firma onefile con manifest corregido | Daniel Arbeláez | SHA256 post-firma definitivo: `CD0D9EFBE36BAC8FBE68DEB80B944048CBFD0157EB78E791328CC90509A2CCBC`. Timestamp DigiCert 2026-04-15 21:07:40 |
| _pendiente_ | Envío reporte FP a Microsoft WDSI | — | ticket ID de WDSI |
| _pendiente_ | Solicitud whitelist a SOC | — | radicado de correo |
| _pendiente_ | Decisión sobre CA comercial (OV vs EV) | — | cotización adjunta |

---

## 5. Referencias técnicas

- Microsoft WDSI (reporte falsos positivos): https://www.microsoft.com/en-us/wdsi/filesubmission
- CA/Browser Forum — Code Signing Baseline Requirements (v3.5, 2024)
- Microsoft Trusted Root Program — lista vigente de CAs
- PyInstaller False Positive tracker: https://github.com/pyinstaller/pyinstaller/issues/5932
