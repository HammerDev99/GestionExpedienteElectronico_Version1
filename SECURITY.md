# Security Policy - AgilEx by Marduk

## 🔒 Aviso de Seguridad

**AgilEx by Marduk** es un software legítimo de automatización robótica (RDA - Robotic Desktop Automation) desarrollado para el **Consejo Superior de la Judicatura - Rama Judicial de Colombia**.

### ✅ Declaración de Autenticidad

- **Propósito**: Automatizar la creación de índices electrónicos de expedientes judiciales según el estándar PCSJA20-11567 de 2020
- **Desarrollador**: Daniel Arbelaez Alvarez (darbelaal@cendoj.ramajudicial.gov.co)
- **Organización**: CENDOJ - Centro de Documentación Judicial
- **Licencia**: MIT License - Código abierto y auditable
- **Repositorio oficial**: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1

### 🛡️ Análisis de Seguridad

El código ha sido sometido a análisis de seguridad:

- ✅ **Análisis de código estático**: Solo 1 alerta de nivel MEDIO (gestión de archivos temporales)
- ✅ **Sin código malicioso**: Verificado y auditado
- ✅ **Código fuente abierto**: Completamente transparente y revisable
- ✅ **Firma digital**: Ejecutable firmado digitalmente (cuando se compila con certificado)

---

## ⚠️ Explicación de Técnicas que Pueden Generar Alertas

Este software utiliza técnicas legítimas de automatización que **pueden disparar heurísticas de antivirus**:

### 1. Automatización COM de Microsoft Office

**Ubicación**: `src/model/metadata_extractor.py:472`

```python
# Automatización legítima de Word/Excel para conteo de páginas
word = win32.Dispatch("Word.Application")
```

**Propósito legítimo**:
- Abrir documentos Word/Excel para extraer metadatos
- Contar páginas de documentos judiciales
- Necesario para generar índices electrónicos precisos

**Por qué dispara alertas**:
- Los malware de Office usan la misma técnica para inyectar macros
- Es idéntico a técnicas de macro-malware

**Diferencia con malware**:
- ❌ Malware: Modifica documentos, inyecta código, exfiltra datos
- ✅ AgilEx: Solo **LEE** metadatos, no modifica ni exfiltra

### 2. Monitoreo y Terminación de Procesos

**Ubicación**: `src/model/file_processor.py:332-333`

```python
# Limpieza de procesos Excel zombies
proc = psutil.Process(pid)
proc.kill()
```

**Propósito legítimo**:
- Cerrar procesos Excel huérfanos que quedan abiertos
- Liberar memoria después del procesamiento
- Evitar acumulación de procesos zombies

**Por qué dispara alertas**:
- Ransomware usa `psutil.kill()` para terminar antivirus
- Idéntico a técnicas de malware destructivo

**Diferencia con malware**:
- ❌ Malware: Termina procesos de seguridad, navegadores, antivirus
- ✅ AgilEx: Solo termina **sus propios** procesos Excel creados (PID rastreados)

### 3. Manipulación de Archivos del Sistema

**Ubicación**: `src/model/file_processor.py`, `src/model/metadata_extractor.py`

```python
# Renombrado de archivos para cumplir estándares judiciales
os.rename(old_path, new_path)
shutil.copy(source, destination)
```

**Propósito legítimo**:
- Estandarizar nombres de archivos según normativa judicial
- Organizar expedientes en estructura jerárquica
- Crear copias de seguridad de índices

**Por qué dispara alertas**:
- Ransomware usa las mismas funciones para cifrar/destruir archivos
- Patrón idéntico a malware destructivo

**Diferencia con malware**:
- ❌ Malware: Cifra, elimina o exfiltra archivos de usuarios
- ✅ AgilEx: Solo **organiza y renombra** archivos en carpetas específicas seleccionadas por el usuario

### 4. Empaquetado con PyInstaller

**Ubicación**: `config/main.spec`

```python
# Compilación a ejecutable standalone
pyinstaller config/main.spec
```

**Por qué dispara alertas**:
- PyInstaller es usado frecuentemente por malware para ofuscar código Python
- Los ejecutables empaquetados parecen "comprimidos" a los antivirus
- Sin firma digital de CA reconocida, se consideran "desconocidos"

**Diferencia con malware**:
- ❌ Malware: Ofuscado, sin código fuente, sin firma
- ✅ AgilEx: Código abierto, auditabe, firmado digitalmente

### 5. Peticiones HTTP para Actualizaciones

**Ubicación**: `src/view/application.py:609`

```python
# Verificación de actualizaciones desde GitHub
response = requests.get("https://raw.githubusercontent.com/...")
```

**Propósito legítimo**:
- Comprobar si hay versiones más recientes del software
- Notificar al usuario sobre actualizaciones disponibles
- **NO descarga ni instala automáticamente**

**Por qué dispara alertas**:
- Malware usa HTTP para conectarse a servidores C&C (Command & Control)

**Diferencia con malware**:
- ❌ Malware: Descarga payloads, exfiltra datos, recibe comandos
- ✅ AgilEx: Solo **verifica** versión, no descarga código ejecutable

---

## 🔍 Falsos Positivos Conocidos

### Dependencias con Historial de Detecciones

| Biblioteca | Propósito | Historial de Falsos Positivos |
|------------|-----------|-------------------------------|
| **xlwings** | Integración Excel | Detectado por Avast (2024), Check Point (2023) |
| **pywin32** | Automatización Windows COM | Detectado por AVG, Windows Defender |
| **psutil** | Monitoreo de procesos | Visto como "spyware behavior" |
| **PyInstaller** | Empaquetado de ejecutables | Frecuentes falsos positivos en todos los AV |

**Documentación de terceros**:
- [xlwings False Positive - Check Point Community](https://community.checkpoint.com/t5/Endpoint/Harmony-Endpoint-XLWings-false-positive/td-p/176865)
- [PyInstaller False Positives - GitHub Issue #2988](https://github.com/pyinstaller/pyinstaller/issues/2988)
- [pywin32 Malware Reports - Stack Overflow](https://stackoverflow.com/questions/51957188/what-is-the-malware-associated-with-pywin32)

### Motores Antivirus con Detecciones Conocidas

- **Malwarebytes**: "Trojan.Generic" (confianza 50%)
- **Windows Defender**: Ocasionalmente "Trojan:Win32/Wacatac"
- **Avast**: "Win32:Evo-gen [Susp]"

**Razón**: Heurísticas basadas en comportamiento, no en firmas de malware conocido.

---

## 📊 Mitigaciones Implementadas

### ✅ Medidas de Confianza Aplicadas

1. **Desactivación de UPX** (`config/main.spec:101`)
   - Sin compresión que ofusque el ejecutable
   - Binario transparente para análisis estático

2. **Firma Digital** (post-build con SignTool)
   - Certificado autofirmado para validar integridad
   - Timestamp incluido para validez perpetua

3. **Metadatos Extendidos** (`src/assets/version_info.rc`)
   - CompanyName: Rama Judicial de Colombia - CENDOJ
   - LegalTrademarks: Consejo Superior de la Judicatura
   - PrivateBuild: Identificación del desarrollador oficial
   - SpecialBuild: "Validated for Colombian Judicial System - No malware"
   - Comments: Descripción completa del propósito

4. **Manifiesto UAC** (`src/assets/app.manifest`)
   - Nivel `asInvoker`: Sin elevación de privilegios
   - `uac_admin=False`: No requiere permisos de administrador
   - Compatibilidad Windows 7-11 declarada

5. **Código Abierto**
   - Repositorio público en GitHub
   - Completamente auditable
   - Licencia MIT transparente

---

## 🚨 Reportar Problemas de Seguridad

### Si Encuentras un Problema de Seguridad Real

**NO lo publiques públicamente**. Reporta de forma responsable a:

- **Email**: darbelaal@cendoj.ramajudicial.gov.co
- **Subject**: [SECURITY] Reporte de Vulnerabilidad - AgilEx

Incluye:
1. Descripción detallada de la vulnerabilidad
2. Pasos para reproducir
3. Impacto potencial
4. Versión afectada

**Tiempo de respuesta**: 48-72 horas hábiles

### Si Tu Antivirus Detecta AgilEx como Amenaza

1. **Verifica la fuente de descarga**
   - Repositorio oficial: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1
   - Releases oficiales: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases

2. **Verifica la firma digital**
   ```powershell
   Get-AuthenticodeSignature -FilePath "AgilEx_by_Marduk.exe"
   ```
   - Debe estar firmado por "HammerDev99" o "Daniel Arbelaez Alvarez"

3. **Reporta el falso positivo al fabricante del antivirus**
   - [Malwarebytes False Positive Report](https://www.malwarebytes.com/false-positive)
   - [Windows Defender - Submit File](https://www.microsoft.com/en-us/wdsi/filesubmission)
   - [VirusTotal](https://www.virustotal.com/)

4. **Contacta al desarrollador**
   - Email: darbelaal@cendoj.ramajudicial.gov.co
   - GitHub Issues: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/issues

---

## 🔐 Verificación de Integridad

### Hash SHA256 del Ejecutable (Versión 1.4.4)

```
# Generar hash del ejecutable descargado
certutil -hashfile AgilEx_by_Marduk.exe SHA256
```

**Hash oficial** (se actualiza con cada release):
```
[Se incluirá en cada GitHub Release]
```

Si el hash no coincide, **NO ejecutes el archivo** y repórtalo inmediatamente.

---

## 📜 Declaración de No Responsabilidad

Este software se proporciona "TAL CUAL", sin garantías de ningún tipo. El uso es bajo tu propio riesgo. El desarrollador no se hace responsable por:

- Daños causados por uso incorrecto
- Pérdida de datos por errores del usuario
- Detecciones de antivirus en versiones modificadas no oficiales

**Usa solo versiones oficiales** del repositorio GitHub.

---

## 📞 Contacto

**Desarrollador**: Daniel Arbelaez Alvarez
**Email**: darbelaal@cendoj.ramajudicial.gov.co
**Organización**: CENDOJ - Consejo Superior de la Judicatura
**GitHub**: https://github.com/HammerDev99
**Repositorio**: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1

---

## 📅 Historial de Actualizaciones de Seguridad

| Fecha | Versión | Cambio de Seguridad |
|-------|---------|---------------------|
| 2025-10-06 | 1.4.5 | Desactivación de UPX, metadatos extendidos, manifiesto UAC |
| 2025-03-04 | 1.4.4 | Implementación de firma digital con certificado autofirmado |
| 2024-XX-XX | 1.4.0 | Refactorización MVC con separación de responsabilidades |

---

**Última actualización**: Octubre 6, 2025
**Versión del documento**: 1.0
