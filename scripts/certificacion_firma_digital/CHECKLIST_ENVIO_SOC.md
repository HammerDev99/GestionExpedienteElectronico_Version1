# Checklist de envío al SOC — Incidente 804977

> **Fecha de preparación:** 2026-04-20
> **Contexto:** Envío acordado en reunión técnica con el SOC para que ejecuten pruebas estáticas y dinámicas.
> **Binario final:** `dist/AgilEx_by_Marduk.exe` firmado, SHA256 `09657C47EB8657838E1B75C413185247543D479A0B14F90E45D4F62CAB7E1BF7`

---

## 1. Documentos listos para enviar

Todos ubicados en `scripts/certificacion_firma_digital/`:

### 1.1 Cuerpo del correo (copiar al cliente de correo)

| Archivo | Ubicación | Propósito |
|---|---|---|
| `correo_ejecutivo_soc.md` | `plantillas/` | Versión Markdown con metadatos |
| `correo_ejecutivo_soc.txt` | `plantillas/` | Versión texto plano para copy-paste directo |

### 1.2 Adjuntos al correo (desde `evidencias/`)

| # | Archivo | Tamaño | Propósito | Estado |
|---|---|---|---|---|
| 1 | `informe_tecnico_soc.pdf` | 334 KB | Informe técnico detallado (guía del análisis del SOC) | ✅ |
| 2 | `../../dist/AgilEx_by_Marduk.exe` | 48.54 MB | Binario firmado para análisis dinámico | ✅ |
| 3 | `cert_public.cer` | 1.5 KB | Certificado público DER | ✅ |
| 4 | `hash_sha256.txt` | <1 KB | Hash y metadatos del binario | ✅ |
| 5 | `virustotal/virustotal_result.txt` | 4.7 KB | Resumen análisis VirusTotal | ✅ |
| 6 | `alerta_xdr.pdf` | 255 KB | Consolidado 3 capturas incidente 804977 | ✅ |
| 7 | `respuesta_andes_scd_2026-04-20.txt` | 6.5 KB | Validación técnica del cert comercial en trámite | ✅ |

**Tamaño total aproximado:** 49.2 MB (el `.exe` domina). Si el servidor del correo institucional tiene límite de 25 MB, enviar el `.exe` por canal alterno (WeTransfer, OneDrive, compartir link interno) e incluir la URL y el hash en el cuerpo del correo.

### 1.3 Anexo opcional (si el SOC pide la carta formal)

| Archivo | Ubicación | Cuándo enviar |
|---|---|---|
| `solicitud_whitelist_soc_FINAL.docx` | `evidencias/` | Si el SOC pide solicitud formal de whitelist además del informe |

---

## 2. Validación cruzada de datos (ya verificada)

| Dato | Valor oficial | Verificado en |
|---|---|---|
| **SHA256 binario** | `09657C47EB8657838E1B75C413185247543D479A0B14F90E45D4F62CAB7E1BF7` | `hash_sha256.txt`, `informe_tecnico_soc.pdf`, `correo_ejecutivo_soc.md/.txt`, `cuerpo_correo_soc.md`, `solicitud_soc_FINAL.md`, `reporte_wdsi_FINAL.md` |
| **Thumbprint** | `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1` | Mismos archivos |
| **Subject cert** | `CN=Daniel Arbelaez Alvarez, OU=AgilEx by Marduk, L=Bogota, S=Bogota D.C., C=CO, E=darbelaal@cendoj.ramajudicial.gov.co` | Mismos archivos + `Get-AuthenticodeSignature` del exe |
| **Vigencia cert** | 2026-04-15 a 2029-04-15 | Mismos archivos |
| **Versión software** | 1.5.1 | `src/assets/version_info.rc`, `src/assets/app.manifest`, `src/assets/last_version.json`, `README.md`, documentos |
| **Tamaño binario** | 50.912.912 bytes | `dist/AgilEx_by_Marduk.exe` |

Comando de re-validación en cualquier momento:

```powershell
$exe = "C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\dist\AgilEx_by_Marduk.exe"
Get-FileHash $exe -Algorithm SHA256
Get-AuthenticodeSignature $exe | Format-List Status, SignerCertificate
```

El resultado esperado:
- `Hash`: `09657C47EB8657838E1B75C413185247543D479A0B14F90E45D4F62CAB7E1BF7`
- `Status`: `UnknownError` (esperado en cert autofirmado — la cadena no llega a raíz Microsoft, pero **la firma es íntegra y el binario no fue modificado**)
- `SignerCertificate.Thumbprint`: `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1`

---

## 3. Campos a completar antes de enviar el correo

- [ ] Teléfono de contacto (reemplazar `[completar antes de enviar]` en el correo)
- [ ] Opcional: cargo/dependencia institucional bajo el nombre
- [ ] Opcional: copiar a jefe inmediato y/o coordinador de sistemas de la seccional
- [ ] Decidir modalidad de envío del `.exe` (adjunto directo o link externo + hash)

---

## 4. Paso a paso del envío

1. **Abrir cliente de correo institucional** (Outlook Web / Outlook Desktop).
2. **Crear nuevo correo**.
3. **Completar metadatos** desde `correo_ejecutivo_soc.md` (Para, CC, Asunto).
4. **Copiar el cuerpo** desde `correo_ejecutivo_soc.txt` (texto plano) y pegarlo directamente.
5. **Reemplazar** `[completar antes de enviar]` por el teléfono de contacto.
6. **Adjuntar los 7 archivos** listados en la sección 1.2.
7. **Verificar** que el tamaño total no exceda el límite del servidor. Si excede:
   - Subir `AgilEx_by_Marduk.exe` a canal alterno (WeTransfer, OneDrive corporativo).
   - Incluir en el cuerpo la URL de descarga y confirmar que el SHA256 coincide con el documentado.
8. **Enviar**.
9. **Guardar radicado** del correo en `evidencias/radicado_soc.txt` con fecha/hora y personas que recibieron.

---

## 5. Seguimiento post-envío

- **Día 0 (día del envío):** confirmar recepción vía correo o llamada telefónica al coordinador del SOC.
- **Día +5 hábiles:** verificar si el SOC ya inició pruebas estáticas/dinámicas. Preguntar por tiempos estimados.
- **Día +10 hábiles:** pedir status de la excepción/whitelist. Si el SOC solicita información complementaria, atender.
- **Paralelo:** avanzar con la solicitud formal de cotización a Andes SCD (certificado EV definitivo).

---

## 6. Si el SOC pide información adicional

Archivos de referencia ya preparados en `plantillas/`:

- `reporte_wdsi_FINAL.md` — reporte del falso positivo a Microsoft WDSI (en caso de que el SOC pida copia o trazabilidad hacia Microsoft)
- `solicitud_whitelist_soc_FINAL.docx` — carta formal jurídico-técnica de solicitud de whitelist (si el SOC la pide como documento oficial)
- `cuerpo_correo_soc.md` — versión más técnica/formal del correo, si prefieren un segundo correo especifico de solicitud
- `preguntas_andes_scd.md` — contexto de la validación técnica del certificado comercial

---

## 7. Riesgos conocidos y respuestas preparadas

| Riesgo | Respuesta |
|---|---|
| El SOC bloquea el `.exe` adjunto en el gateway de correo | Subirlo a OneDrive/WeTransfer y enviar solo el link + hash |
| El SOC pide firma EV comercial antes de whitelist | Referenciar la ruta de Andes SCD (validada 2026-04-20). Tiempo estimado de adquisición y emisión a documentar tras cotización formal |
| El SOC cuestiona la autofirma ("editor desconocido") | El `informe_tecnico_soc.pdf` (sección 2.3) explica qué garantiza y qué no la autofirma; la solución definitiva es el EV en trámite |
| El SOC solicita SBOM o análisis formal del bootloader PyInstaller | Remitir al código fuente público en GitHub y al `requirements.txt`; ofrecer compilar un build con `--debug` para el análisis |
| El tamaño del `.exe` excede el límite del gateway | Canal alterno (OneDrive institucional preferido) con link firmado + hash |

---

## 8. Trazabilidad del paquete de envío

| Elemento | Hash / ID | Fecha |
|---|---|---|
| `AgilEx_by_Marduk.exe` v1.5.1 | SHA256 `09657C47...CAB7E1BF7` | 2026-04-20 15:18 |
| `AgilEx_by_Marduk.exe` v1.5.0 (histórico) | SHA256 `CD0D9EFB...09A2CCBC` | 2026-04-15 21:07 |
| Certificado firmante | Thumbprint `92ADA07A...7D57B1` | Emitido 2026-04-15 |
| Informe técnico (PDF) | Generado desde `informe_diana.md` | 2026-04-20 |
| Respuesta Andes SCD | Archivada como evidencia | 2026-04-20 |
| Incidente SOC | ID `804977`, alerta `RJ-MDE-MAL-ALERT-002` | 2026-04-06 14:37 UTC |
