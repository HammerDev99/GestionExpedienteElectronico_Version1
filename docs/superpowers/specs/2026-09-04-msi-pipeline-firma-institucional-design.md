# Empaquetado MSI y pipeline de firma institucional — AgilEx by Marduk

> **Fecha:** 2026-09-04
> **Estado:** Diseño aprobado, pendiente de plan de implementación
> **Versión base:** AgilEx 1.5.1
> **Incidente relacionado:** `RJ-MDE-MAL-ALERT-002` / ID `804977` (Microsoft XDR, abril 2026)

## 1. Contexto y problema

AgilEx by Marduk es una solución RDA en producción hace 3.5 años en la Rama Judicial de Colombia. Se distribuye hoy como ejecutable único (`AgilEx_by_Marduk.exe`, PyInstaller onefile) firmado con un certificado autofirmado.

En abril de 2026, Microsoft XDR marcó el binario como `Malgent` en un equipo de la Rama Judicial. La causal declarada por el SOC fue "comportamiento, firma digital o reputación". La gestión de ese incidente está documentada en `scripts/certificacion_firma_digital/`.

El área de Seguridad Informática de la Unidad de Transformación Digital requiere que el software se distribuya como paquete `.msi`, firmado por ellos con el certificado institucional, y comprimido en `.rar` para distribución interna.

### 1.1 Propuesta descartada del área de seguridad

El área propuso inicialmente generar una llave que la aplicación validara contra Directorio Activo en tiempo de ejecución, para evitar el bloqueo.

Esta propuesta no resuelve el problema y se descarta por dos razones técnicas:

1. **Opera en la capa equivocada.** El bloqueo XDR/ASR/AppLocker ocurre en el cargador de Windows y en Defender for Endpoint, antes de que el código Python ejecute su primera instrucción. Una validación en tiempo de ejecución llega después de que el proceso ya fue terminado.
2. **No es un control de confianza.** Una llave embebida en un binario distribuido es extraíble mediante análisis estático, y constituiría un hallazgo en una auditoría de seguridad.

El mecanismo correcto para la intención declarada es la firma Authenticode con certificado institucional, complementada con reglas de AppLocker/WDAC por publisher. Una sola regla que confíe en el certificado institucional cubre esta y todas las versiones futuras de AgilEx sin intervención adicional.

### 1.2 Restricciones heredadas

| Restricción | Origen | Implicación |
|---|---|---|
| Build **onefile** obligatorio | Regresión documentada 2026-04-15 (Hallazgo 5) | `onedir` expone ~40-60 DLLs sin firma que ASR/AppLocker evalúan individualmente y bloquean |
| Dependencia de Excel vía COM (xlwings) | Arquitectura del producto | Descarta MSIX (virtualización de registro/FS rompe COM cross-process) |
| Sistema en producción 3.5 años | Operación institucional | Todo cambio de código requiere validación de equivalencia funcional |
| Incidente 804977 abierto | SOC Rama Judicial | El instalador debe minimizar comportamientos que un XDR puntúe |

## 2. Decisiones adoptadas

| # | Decisión | Alternativas descartadas |
|---|---|---|
| D1 | **WiX Toolset v6** como generador de MSI | Advanced Installer/InstallShield (licencia comercial innecesaria); MSIX (rompe COM/xlwings); Inno Setup/NSIS (no producen MSI, no desplegables por GPO) |
| D2 | **El área de Seguridad Informática firma ambos artefactos** con certificado institucional | Firma del desarrollador (el autofirmado no encadena a raíz confiable) |
| D3 | **Certificado EV de Andes SCD descartado** | Consecuencia directa de D2 |
| D4 | **Script único ejecutado íntegramente por ellos**, sin ida y vuelta | Ciclo cruzado (añade una vuelta de correo institucional por release) |
| D5 | **Paquete de entrega autocontenido** con el `.exe` ya compilado | Acceso al repo (exigiría Python/PyInstaller/Excel en su entorno y rompería la trazabilidad por hash) |
| D6 | **Instalación per-machine en `Program Files`** | Per-user en `%LOCALAPPDATA%` (ruta de baja confianza según Hallazgo 5); modo dual (complejidad innecesaria) |
| D7 | **Corrección de rutas de escritura antes de empaquetar** (dos fases) | Fase única (diagnóstico ambiguo ante fallos); instalar fuera de `Program Files` (contradice el objetivo de seguridad) |

## 3. Arquitectura

### 3.1 Frontera de responsabilidad

```
╔═══════════ TRAMO 1 — Desarrollo ═══════════╗
│  build_and_sign.ps1 -SkipSign               │
│         ↓                                   │
│  dist/AgilEx_by_Marduk.exe   (SIN firmar)   │
│         ↓                                   │
│  new-delivery-package.ps1                   │
│         ↓                                   │
│  AgilEx_v<ver>_paquete_firma.zip            │
│    ├── bin/AgilEx_by_Marduk.exe             │
│    ├── wix/Product.wxs                      │
│    ├── build-signed-msi.ps1                 │
│    ├── MANIFIESTO.txt   (SHA256 pre-firma)  │
│    └── README_SEGURIDAD.md                  │
╚═════════════════════════════════════════════╝
                  ↓ entrega formal
╔═══ TRAMO 2 — Seguridad Informática ════════╗
│  .\build-signed-msi.ps1 -Thumbprint <cert>  │
│    0. Preflight (herramientas + cert)       │
│    1. Verifica SHA256 vs MANIFIESTO         │
│    2. signtool → firma .exe   (uso diario)  │
│    3. wix build → .msi                      │
│    4. signtool → firma .msi   (instalación) │
│    5. Rar.exe → comprime                    │
│    6. REPORTE_FIRMA.txt (evidencia)         │
│         ↓                                   │
│  AgilEx_v<ver>_firmado.rar → distribución   │
╚═════════════════════════════════════════════╝
```

### 3.2 Fundamento de las decisiones estructurales

**Por qué se firman dos artefactos.** Un MSI no es un envoltorio de ejecución: es una base de datos de instalación que extrae el `.exe` a disco. Tras la instalación, el MSI deja de participar; lo que se ejecuta a diario es el `.exe` en `Program Files`. Firmar solo el MSI protege el momento de la instalación pero deja intacto el escenario del incidente 804977, que ocurre en el uso diario. Ambos artefactos deben firmarse.

**Por qué el orden de firma es obligatorio.** El `.exe` debe firmarse antes de entrar al CAB del MSI. Un MSI firmado es inmutable: alterar su contenido después de firmarlo invalida la firma.

**Por qué el `.exe` viaja sin firmar con hash declarado.** `MANIFIESTO.txt` contiene el SHA256 del binario tal como salió del build. El script lo verifica antes de firmar y aborta si no coincide. Esto protege el traslado y da al área de seguridad una base defendible: firman exactamente el artefacto declarado.

**Carácter aditivo.** El flujo actual (`build_and_sign.ps1` con certificado autofirmado) no se modifica ni se retira. Sigue disponible para pruebas locales y para el envío pendiente al SOC.

### 3.3 Nota de trazabilidad

Al firmar el `.exe` con el certificado institucional, su SHA256 cambia respecto al `09657C47EB8657838E1B75C413185247543D479A0B14F90E45D4F62CAB7E1BF7` documentado ante el SOC para la versión 1.5.1. Este cambio es esperado y debe comunicarse explícitamente al SOC para que no se interprete como discrepancia. Se documenta en `README_SEGURIDAD.md` y en `REPORTE_FIRMA.txt`.

## 4. Fase A — Corrección de rutas de escritura

### 4.1 Bloqueantes identificados

**Bloqueante 1 (crítico) — `src/model/logger_config.py:9`**

```python
log_dir = "logs"          # relativo al CWD
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # PermissionError en Program Files
```

Instalado en `Program Files` y lanzado desde un acceso directo, el CWD es el directorio de instalación. `os.makedirs` lanza `PermissionError` durante `setup_logger()`, antes de que exista la GUI. La aplicación no abre y el usuario no recibe mensaje de error.

**Bloqueante 2 (menor) — `src/view/tools_launcher.py:15`**

```python
def create_tool_images(output_dir="src/assets/tools"):
    os.makedirs(output_dir, exist_ok=True)
```

Escribe imágenes de placeholder dentro del árbol de la aplicación. Afecta la ventana de herramientas, no el arranque.

### 4.2 Solución

**Bloqueante 1.** Extender `ResourceManager` (`src/utils/resource_manager.py`) con `get_writable_path()`. Se extiende esa clase en lugar de crear un módulo nuevo porque ya es el punto único de resolución de rutas y ya distingue entorno empaquetado de desarrollo; la asimetría faltante es lectura vs. escritura.

Resolución por entorno:

| Entorno | Destino |
|---|---|
| Empaquetado (`sys.frozen`) | `%LOCALAPPDATA%\AgilEx\logs` |
| Desarrollo | `./logs` (comportamiento actual sin cambios) |
| Fallback 1 | `tempfile.gettempdir()` |
| Fallback 2 | Solo handler de consola |

`%LOCALAPPDATA%` es la convención de Windows para datos de aplicación por usuario, es escribible sin privilegios, y sobrevive a la desinstalación (los logs son evidencia de diagnóstico).

**Principio rector: el logging nunca debe impedir que la aplicación arranque.** Hoy sí puede, y esa es una fragilidad latente incluso sin MSI.

**Bloqueante 2.** La corrección no es redirigir la escritura sino eliminarla: las imágenes son estáticas y `Banco1.png` ya viaja en el bundle vía `config/main.spec`. `create_tool_images()` queda como utilidad de desarrollo; la ventana de herramientas lee del bundle mediante `ResourceManager`, con un placeholder en memoria si un archivo falta.

### 4.3 Alcance explícito

**No se modifican:** `file_processor.py`, `process_strategy.py`, `processing_context.py`, `application.py`, ni el flujo Excel/xlwings. La escritura de `file_processor.py:274` (`wb.save()`) opera sobre el expediente seleccionado por el usuario, no sobre el directorio de la aplicación, y no se ve afectada por la instalación en `Program Files`.

## 5. Fase B — Instalador WiX

### 5.1 Identidad del producto

| GUID | Regla | Propósito |
|---|---|---|
| `UpgradeCode` | **Fijo de por vida**, versionado en `.wxs` con comentario de advertencia | Permite reconocer actualizaciones del mismo producto |
| `ProductCode` | Regenerado por release (`Product Id="*"`) | Identifica la versión concreta |
| `Package Id` | Automático | Por compilación |

Modificar el `UpgradeCode` tras la primera distribución rompe la cadena de actualizaciones en todos los endpoints desplegados.

### 5.2 Estrategia de actualización

- `MajorUpgrade` con `Schedule="afterInstallInitialize"`: desinstala la versión anterior antes de instalar la nueva. Evita estados híbridos de archivos entre versiones.
- `AllowDowngrades="no"` con mensaje explícito.

**Regla operativa de versionado:** MSI compara solo los tres primeros campos de la versión. Todo release distribuido debe incrementar alguno de los tres primeros campos (`1.5.1` → `1.5.2` o superior). Un `1.5.1.1` sería indistinguible de `1.5.1` para el motor de actualización. Esto es compatible con el SemVer ya usado por el proyecto.

### 5.3 Componentes

| Componente | Contenido | Notas |
|---|---|---|
| `CmpMainExecutable` | `AgilEx_by_Marduk.exe` en `INSTALLFOLDER` | `KeyPath` del componente |
| `CmpStartMenuShortcut` | Acceso directo Menú Inicio + `RemoveFolder` | Se limpia al desinstalar |
| `CmpDesktopShortcut` | Acceso directo en escritorio | |

- `INSTALLFOLDER` = `ProgramFiles64Folder\AgilEx by Marduk`
- `InstallScope="perMachine"` — elevación al instalar, no al ejecutar
- Los accesos directos per-machine requieren una entrada de registro en `HKLM` como `KeyPath` para validación ICE correcta. Omitirlo produce advertencias que un área de seguridad puede interpretar como paquete mal formado.

### 5.4 Metadatos ARP

`ARPCONTACT`, `ARPURLINFOABOUT` (repositorio), `ARPPRODUCTICON` (`law_logo.ico`), publicador `Daniel Arbelaez Alvarez`, `ARPNOMODIFY`.

Deben ser coherentes con `src/assets/version_info.rc` y con el Subject del certificado. La inconsistencia entre metadatos PE, certificado y MSI fue identificada como factor de sospecha heurística en `HALLAZGOS_CERT_ACTUAL.md` (Hallazgo 2).

### 5.5 Instalación silenciosa

`msiexec /i AgilEx.msi /qn /l*v install.log` debe completarse sin interacción. Es el requisito que habilita despliegue por GPO/SCCM; sin él el MSI pierde su propósito institucional.

UI interactiva: `WixUI_InstallDir` mínima (bienvenida, licencia MIT, ruta, confirmación). Sin pantallas de configuración — no hay nada configurable y cada pantalla adicional es superficie de fallo en instalación desatendida.

### 5.6 Comportamientos deliberadamente excluidos

| Excluido | Razón |
|---|---|
| Verificación de Excel instalado | Abortaría despliegues por GPO donde Excel se instala en otro orden. Si se requiere, va como advertencia, nunca como bloqueo |
| Auto-actualización desde el instalador | Tráfico saliente desde proceso elevado es un patrón que dispara XDR. La app ya consulta `last_version.json` en runtime |
| Registro de tipos de archivo | Innecesario |
| Servicios o tareas programadas | Innecesario; superficie de sospecha |
| Escritura en registro más allá del `KeyPath` | Innecesario |

Un instalador que solo copia un archivo firmado y crea dos accesos directos es el perfil de menor sospecha posible ante un XDR.

## 6. Fase B — Script `build-signed-msi.ps1`

### 6.1 Principio de diseño

**El script no toma decisiones.** No elige certificado, no infiere rutas, no reintenta, no corrige. Valida, ejecuta seis pasos en orden y, ante cualquier anomalía, se detiene con un mensaje accionable.

Esta restricción se deriva del contexto de ejecución: lo opera personal que no lo escribió, en una máquina que el desarrollador no controla, sin capacidad de depurarlo.

### 6.2 Invocación

```powershell
.\build-signed-msi.ps1 -Thumbprint "A1B2C3..."
```

Opcionales: `-TimestampUrl` (default: DigiCert), `-SkipRar`, `-OutputDir`.

### 6.3 Etapas

| # | Etapa | Verificación | Exit code |
|---|---|---|---|
| 0 | Preflight | `signtool`, `wix`, `Rar.exe` presentes; thumbprint existente, vigente, con EKU Code Signing; **determinación de si el certificado es autofirmado** (Subject == Issuer) para fijar el criterio de verificación de §6.5 | 10 |
| 1 | Integridad | SHA256 de `bin/*.exe` == `MANIFIESTO.txt` | 20 |
| 2 | Firma `.exe` | `Get-AuthenticodeSignature` posterior | 30 |
| 3 | Build MSI | `wix build`, versión leída de `version_info.rc` | 40 |
| 4 | Firma `.msi` | `Get-AuthenticodeSignature` posterior | 50 |
| 5 | Compresión RAR | No fatal — ver 6.4 | — |
| 6 | Reporte | Generación de `REPORTE_FIRMA.txt` | — |

Comando de firma:

```
signtool sign /sha1 <thumbprint> /fd SHA256 /td SHA256 /tr <timestamp_url> [/d "AgilEx by Marduk"]
```

Timestamp RFC 3161 obligatorio: mantiene válida la firma tras la expiración del certificado.

### 6.4 Tolerancia de la etapa RAR

`Rar.exe` no está en `PATH` por defecto. El script lo busca en las rutas conocidas de WinRAR (`%ProgramFiles%\WinRAR\Rar.exe`, `%ProgramFiles(x86)%\WinRAR\Rar.exe`). Si no lo encuentra, **no falla el proceso**: deja el MSI firmado y emite advertencia. La compresión es el último eslabón y no justifica perder una firma exitosa.

Comando: `Rar.exe a -m5 -ep1`

### 6.5 Manejo de estados de firma

`Get-AuthenticodeSignature` devuelve estados distintos según el certificado:

| Estado | Certificado | Acción del script |
|---|---|---|
| `Valid` | Institucional (encadena a raíz confiable) | Continúa |
| `UnknownError` | Autofirmado (firma íntegra, cadena incompleta) | Advierte y continúa **solo si** se invocó con un certificado autofirmado detectado en preflight |
| Otros | — | Aborta |

Esta distinción es necesaria para que el script pueda probarse con el certificado autofirmado actual (thumbprint `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1`) sin debilitar la verificación real en manos del área de seguridad.

### 6.6 Restricciones de comportamiento

El script **no**: accede a internet salvo la URL de timestamp (documentada), lee o escribe fuera de su carpeta, requiere privilegios de administrador, modifica el almacén de certificados, ni compila código Python.

Debe ser legible de arriba abajo por un auditor de seguridad antes de su ejecución.

### 6.7 Evidencia generada

`REPORTE_FIRMA.txt` contiene: hashes antes y después de cada firma, thumbprint, Subject y vigencia del certificado, sello de tiempo, salida de verificación de ambos artefactos, versión del producto y fecha de ejecución. Se anexa al expediente del incidente 804977 y permite reverificación posterior independiente.

Transcript completo de la ejecución a archivo, para diagnóstico remoto ante fallos.

### 6.8 `README_SEGURIDAD.md`

Dirigido a un lector sin conocimiento previo del proyecto: qué es AgilEx (3 líneas), qué hace el script paso a paso, prerequisitos, comando exacto, salida esperada, tabla de códigos de error, nota sobre el cambio de SHA256 (§3.3) y vínculo con el incidente 804977.

## 7. Estrategia de verificación

### 7.1 Nivel 1 — Unitario (Fase A)

Pytest sobre `get_writable_path()`:

- Entorno empaquetado resuelve a `%LOCALAPPDATA%\AgilEx\logs`
- Entorno de desarrollo mantiene `./logs`
- Fallback a temp cuando el destino no es escribible
- **Test de regresión decisivo:** `setup_logger()` no lanza excepción con CWD de solo lectura

### 7.2 Nivel 2 — Integración local (puerta entre fases)

Antes de iniciar la Fase B:

1. El `.exe` compilado se ejecuta desde una carpeta sin permisos de escritura y abre correctamente.
2. Procesamiento real de expediente con las **tres estrategias** (cuaderno único, expediente único, múltiples expedientes) produce un índice Excel equivalente al de la versión 1.5.1.
3. Los logs aparecen en `%LOCALAPPDATA%\AgilEx\logs`.

El punto 2 es la salvaguarda de los 3.5 años de producción: la comparación es contra la salida real de 1.5.1, no contra una expectativa teórica.

### 7.3 Nivel 3 — Instalador en máquina limpia

VM sin Python ni Excel de desarrollo (verifica de paso la autosuficiencia del onefile).

| Escenario | Criterio de aceptación |
|---|---|
| Instalación interactiva | Sin error; ambos accesos directos presentes |
| Instalación silenciosa `/qn` | Sin interacción; exit code 0 |
| Ejecución post-instalación | Abre desde ambos accesos directos; procesa un expediente completo |
| Metadatos ARP | Nombre, versión, publicador e icono correctos |
| Desinstalación | Sin residuos en `Program Files`; sin accesos directos huérfanos |
| Actualización | Versión superior actualiza; **una sola entrada** en ARP |
| Downgrade | Bloqueado con mensaje claro |

La fila de actualización valida el `UpgradeCode`, que es la decisión no corregible a posteriori.

### 7.4 Validación del script de firma

El script se prueba de punta a punta con el certificado autofirmado actual (`92ADA07A…`), ejercitando la misma ruta de código que ejecutará el área de seguridad. La única variable que cambia en sus manos es el certificado. Cuando ellos lo ejecuten por primera vez, no será la primera ejecución del script.

## 8. Despliegue

Escalonado, con evidencia archivada en `scripts/certificacion_firma_digital/evidencias/` en cada etapa:

1. **Entrega a Seguridad Informática** — paquete para su auditoría y ejecución.
2. **Piloto reducido** — grupo limitado de endpoints, incluyendo idealmente el equipo donde se disparó la alerta 804977 (prueba definitiva de cierre del incidente).
3. **Distribución institucional** — GPO/SCCM.

**Criterio de reversión:** el `.exe` firmado actual permanece distribuible. Si el MSI falla en piloto, se retorna a ese canal sin bloquear la operación. El pipeline nuevo es aditivo y el camino existente no se retira hasta que el nuevo esté validado.

## 9. Fuera de alcance

| Elemento | Responsable |
|---|---|
| Regla AppLocker/WDAC por publisher | Área de Seguridad Informática |
| Envío al SOC del incidente 804977 | Gestión en curso, `CHECKLIST_ENVIO_SOC.md` |
| Certificado EV Andes SCD | Descartado por decisión D2/D3 |
| Migración a MSIX | Descartado por incompatibilidad con COM/xlwings |

## 10. Artefactos a producir

| Artefacto | Ubicación | Fase |
|---|---|---|
| `get_writable_path()` | `src/utils/resource_manager.py` | A |
| Logger con ruta escribible | `src/model/logger_config.py` | A |
| Corrección de imágenes de herramientas | `src/view/tools_launcher.py` | A |
| Tests | `src/test/` | A |
| `Product.wxs` | `installer/wix/` | B |
| `build-signed-msi.ps1` | `installer/` | B |
| `new-delivery-package.ps1` | `scripts/` | B |
| `README_SEGURIDAD.md` | `installer/` | B |
