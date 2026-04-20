# AgilEx by Marduk 1.5.1

## 🎯 Lo Nuevo en Esta Versión

> Release de **trazabilidad y seguridad de firma digital** — no introduce cambios funcionales respecto a 1.5.0. El comportamiento y las capacidades de la aplicación permanecen idénticos.

- **Firma digital Authenticode renovada**: certificado self-signed SHA256 (RSA 4096) vigente del 2026-04-15 al 2029-04-15, con marca de tiempo RFC 3161 de DigiCert. Thumbprint estable `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1` durante 3 años, válido como criterio de whitelist ante SOCs institucionales.
- **Compilación definitiva en modo `onefile`**: un único ejecutable sin DLLs sueltas, optimizado para entornos corporativos con Microsoft Defender XDR, Attack Surface Reduction (ASR) y AppLocker activos.
- **Metadatos PE actualizados a 1.5.1.0** (`FileVersion`, `ProductVersion`, `assemblyIdentity`) para trazabilidad explícita del binario ante herramientas de análisis estático y procedimientos de SOC.
- **Identidad jurídica ajustada a persona natural**: `CompanyName="Daniel Arbelaez Alvarez"`, `LegalCopyright` con referencia a Licencia MIT y derechos morales irrenunciables (Ley 23 de 1982, art. 30). Aporte voluntario al Sistema Judicial Colombiano, sin relación contractual.
- **Gestión en curso de certificado EV Code Signing**: validación técnica positiva con Andes SCD (white-label de Sectigo, raíz incluida en el Microsoft Trusted Root Program). Una vez emitido y aplicado, eliminará definitivamente la advertencia "Editor desconocido" de SmartScreen y otorgará reputación inmediata en Microsoft Defender.
- **Validación externa independiente conservada**: VirusTotal 1/72 motores antivirus (detección aislada heurística genérica de Bkav Pro). Microsoft Defender, Kaspersky, ESET, Symantec, Sophos, BitDefender, CrowdStrike, SentinelOne y el resto de motores empresariales referentes = Undetected.

## 🔎 Vista previa

<img width="609" height="728" alt="image" src="https://github.com/user-attachments/assets/c3a69a59-5d43-4130-b9c3-a521f8ac342a" />

## 🚀 Guía Rápida de Uso

1. **Preparación**
   - Descargue las carpetas que requiera procesar
   - Si utiliza almacenamiento en la nube, descargue los archivos localmente y suspenda la sincronización temporalmente
2. **Tipos de Gestión y Estructura Esperada**
   - **Cuaderno**: `C01Principal/Archivos`
   - **Expediente**: `05088/01PrimeraInstancia/C01Principal/Archivos`
   - **Múltiples Expedientes**: `SERIE_SUBSERIE/05088/01PrimeraInstancia/C01Principal/Archivos`
3. **Requisitos Técnicos**
   - Los nombres de archivos deben seguir una secuencia ordenada
   - Cierre todas las hojas de cálculo Excel en ejecución
   - Asegúrese que la ruta completa no exceda los 256 caracteres
   - Introduzca información SGDE exacta (Juzgado y serie/subserie)

## 📝 Verificación de Integridad

**SHA256 del binario firmado:**
```
09657C47EB8657838E1B75C413185247543D479A0B14F90E45D4F62CAB7E1BF7
```

**Verificar en Windows (PowerShell):**
```powershell
Get-FileHash .\AgilEx_by_Marduk.exe -Algorithm SHA256
```

**Certificado firmante:**
- Subject: `CN=Daniel Arbelaez Alvarez, OU=AgilEx by Marduk, L=Bogota, S=Bogota D.C., C=CO, E=darbelaal@cendoj.ramajudicial.gov.co`
- Thumbprint: `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1`
- Vigencia: 2026-04-15 a 2029-04-15
- Algoritmo: Authenticode SHA256 + Timestamp RFC 3161 (DigiCert TSA)

## 🎓 Recursos Adicionales

- [Video Tutorial](https://enki.care/UltimateO)
- [Video Tutorial](https://enki.care/UltimateY)
- [Documentación Agilex by Marduk](https://docs.agilex.sprintjudicial.com/)

---
*Este software cumple con el Protocolo para la gestión de documentos electrónicos, digitalización y conformación del expediente electrónico (PCSJA20-11567 de 2020, Versión 2) y las condiciones archivísticas mínimas para migrar a Alfresco*
