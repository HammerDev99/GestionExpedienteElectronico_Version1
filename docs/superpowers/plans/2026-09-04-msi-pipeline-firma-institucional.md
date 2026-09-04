# Empaquetado MSI y pipeline de firma institucional — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Distribuir AgilEx by Marduk como paquete MSI firmado por el área de Seguridad Informática con certificado institucional, resolviendo el incidente XDR 804977 tanto en la instalación como en el uso diario.

**Architecture:** Dos fases. La Fase A corrige rutas de escritura relativas al CWD que impiden que la aplicación arranque desde `Program Files`. La Fase B construye el instalador WiX y un script autocontenido que el área de Seguridad Informática ejecuta en su entorno para firmar el `.exe`, empaquetar el MSI, firmarlo y comprimirlo, sin ida y vuelta.

**Tech Stack:** Python 3 + PyInstaller (onefile), pytest, WiX Toolset v6 (via `dotnet tool`), PowerShell 5.1+, signtool (Windows SDK 10.0.22621.0), WinRAR.

**Spec:** `docs/superpowers/specs/2026-09-04-msi-pipeline-firma-institucional-design.md`

## Global Constraints

- **Build onefile obligatorio.** Nunca migrar a `onedir`. Regresión documentada 2026-04-15 (Hallazgo 5): ASR/AppLocker bloquean las ~40-60 DLLs sin firma.
- **Versión actual:** `1.5.1` / `1.5.1.0`. Fuente de verdad: `src/assets/version_info.rc`.
- **Regla de versionado MSI:** todo release distribuido debe incrementar alguno de los **tres primeros** campos. `1.5.1.1` es indistinguible de `1.5.1` para el motor de actualización.
- **`UpgradeCode` es inmutable de por vida.** Se genera una sola vez en la Tarea 4 y nunca se modifica.
- **Orden de firma obligatorio:** `.exe` primero, `.msi` después. Un MSI firmado es inmutable.
- **Identidad consistente:** `CompanyName` = `Daniel Arbelaez Alvarez`, `ProductName` = `AgilEx by Marduk - Gestión de Expediente Electrónico`, `OriginalFilename` = `AgilEx_by_Marduk.exe`. Deben coincidir entre `version_info.rc`, MSI y certificado.
- **Certificado autofirmado de pruebas:** thumbprint `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1`, vigente hasta 2029-04-15.
- **Timestamp RFC 3161 por defecto:** `http://timestamp.digicert.com`
- **No modificar:** `file_processor.py`, `process_strategy.py`, `processing_context.py`, `application.py`, ni el flujo Excel/xlwings.
- **Idioma:** código y nombres de identificadores en inglés; mensajes de usuario, comentarios y documentación en español con tildes correctas.
- **Commits:** formato convencional (`feat:`, `fix:`, `docs:`, `test:`, `chore:`).

---

## Estructura de archivos

| Archivo | Responsabilidad | Tarea |
|---|---|---|
| `src/utils/resource_manager.py` (modificar) | Añadir `get_writable_path()` — resolución de rutas escribibles | 1 |
| `src/test/test_resource_manager.py` (crear) | Tests de resolución de rutas escribibles | 1 |
| `src/model/logger_config.py` (modificar) | Usar ruta escribible; nunca impedir el arranque | 2 |
| `src/test/test_logger_config.py` (crear) | Tests de logger, incluida regresión con CWD de solo lectura | 2 |
| `src/view/tools_launcher.py` (modificar) | Eliminar escritura en el árbol de la app; leer del bundle | 3 |
| `installer/wix/Product.wxs` (crear) | Definición del instalador MSI | 4 |
| `installer/build-signed-msi.ps1` (crear) | Script de 6 etapas que ejecuta Seguridad Informática | 5, 6 |
| `installer/README_SEGURIDAD.md` (crear) | Instrucciones para el área de Seguridad Informática | 7 |
| `scripts/new-delivery-package.ps1` (crear) | Genera el ZIP de entrega con MANIFIESTO.txt | 7 |

---

## FASE A — Corrección de rutas de escritura

### Task 1: `get_writable_path()` en ResourceManager

**Files:**
- Modify: `src/utils/resource_manager.py` (añadir método a la clase `ResourceManager`)
- Create: `src/test/test_resource_manager.py`
- Modify: `requirements.txt` (añadir pytest)

**Interfaces:**
- Consumes: `ResourceManager.__init__` existente, que ya define `self.is_frozen` y `self.base_path`.
- Produces: `ResourceManager.get_writable_path(subdir: str = "") -> str` — devuelve una ruta absoluta a un directorio **existente y escribible**, creándolo si hace falta. En entorno empaquetado resuelve bajo `%LOCALAPPDATA%\AgilEx`; en desarrollo, bajo el directorio de trabajo actual. Nunca lanza excepción: si ningún candidato es escribible, devuelve `tempfile.gettempdir()`.

- [ ] **Step 1: Instalar pytest y registrarlo en requirements**

```bash
.venv/Scripts/python.exe -m pip install pytest==8.3.4
```

Añadir al final de `requirements.txt`:

```
pytest==8.3.4
```

- [ ] **Step 2: Escribir el test que falla**

Crear `src/test/test_resource_manager.py`:

```python
import os
import sys
import tempfile

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from utils.resource_manager import ResourceManager


def test_writable_path_in_development_uses_cwd(tmp_path, monkeypatch):
    """En desarrollo la ruta escribible cuelga del directorio actual."""
    monkeypatch.chdir(tmp_path)
    manager = ResourceManager()
    manager.is_frozen = False

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert os.path.samefile(
        os.path.dirname(result), str(tmp_path)
    )


def test_writable_path_when_frozen_uses_localappdata(monkeypatch, tmp_path):
    """Empaquetado, la ruta escribible cuelga de LOCALAPPDATA\\AgilEx."""
    fake_local = tmp_path / "LocalAppData"
    fake_local.mkdir()
    monkeypatch.setenv("LOCALAPPDATA", str(fake_local))

    manager = ResourceManager()
    manager.is_frozen = True

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert "AgilEx" in result
    assert result.endswith("logs")


def test_writable_path_falls_back_to_temp(monkeypatch, tmp_path):
    """Si el destino no es escribible, cae a la carpeta temporal."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "inexistente"))

    manager = ResourceManager()
    manager.is_frozen = True

    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(os, "makedirs", deny)

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert os.path.samefile(result, tempfile.gettempdir())


def test_writable_path_without_subdir_returns_base(monkeypatch, tmp_path):
    """Sin subdirectorio devuelve la carpeta base de datos de usuario."""
    fake_local = tmp_path / "LocalAppData"
    fake_local.mkdir()
    monkeypatch.setenv("LOCALAPPDATA", str(fake_local))

    manager = ResourceManager()
    manager.is_frozen = True

    result = manager.get_writable_path()

    assert os.path.isdir(result)
    assert result.endswith("AgilEx")
```

- [ ] **Step 3: Ejecutar el test y verificar que falla**

Run: `.venv/Scripts/python.exe -m pytest src/test/test_resource_manager.py -v`
Expected: FAIL con `AttributeError: 'ResourceManager' object has no attribute 'get_writable_path'`

- [ ] **Step 4: Implementar el método**

En `src/utils/resource_manager.py`, añadir `import tempfile` junto a los imports existentes y este método dentro de la clase `ResourceManager`, después de `get_path`:

```python
    APP_DATA_FOLDER = "AgilEx"

    def get_writable_path(self, subdir=""):
        """
        Obtiene una ruta escribible para datos generados en ejecución.

        A diferencia de get_path (recursos de solo lectura del bundle),
        esta ruta admite escritura. Necesario porque la aplicación se
        instala en Program Files, donde el directorio de la app es de
        solo lectura.

        Args:
            subdir (str): Subdirectorio opcional (ej. "logs")

        Returns:
            str: Ruta absoluta a un directorio existente y escribible
        """
        candidates = []

        if self.is_frozen:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                candidates.append(
                    os.path.join(local_app_data, self.APP_DATA_FOLDER)
                )
        else:
            candidates.append(os.path.join(os.getcwd(), self.APP_DATA_FOLDER))

        candidates.append(
            os.path.join(tempfile.gettempdir(), self.APP_DATA_FOLDER)
        )

        for candidate in candidates:
            target = os.path.join(candidate, subdir) if subdir else candidate
            try:
                os.makedirs(target, exist_ok=True)
                return os.path.normpath(target)
            except (OSError, PermissionError) as e:
                if self.logger:
                    self.logger.warning(
                        f"Ruta no escribible {target}: {e}"
                    )

        return tempfile.gettempdir()
```

- [ ] **Step 5: Ejecutar los tests y verificar que pasan**

Run: `.venv/Scripts/python.exe -m pytest src/test/test_resource_manager.py -v`
Expected: PASS — 4 tests

- [ ] **Step 6: Commit**

```bash
git add src/utils/resource_manager.py src/test/test_resource_manager.py requirements.txt
git commit -m "feat: agregar get_writable_path a ResourceManager

Resuelve rutas escribibles para datos de ejecucion, necesario porque
la instalacion en Program Files deja el directorio de la app en solo
lectura. Degrada a carpeta temporal si el destino no es escribible."
```

---

### Task 2: Logger con ruta escribible

**Files:**
- Modify: `src/model/logger_config.py:1-40` (reescritura de `setup_logger`)
- Create: `src/test/test_logger_config.py`

**Interfaces:**
- Consumes: `ResourceManager.get_writable_path(subdir)` de la Tarea 1.
- Produces: `setup_logger() -> logging.Logger` — misma firma pública que hoy. Nunca lanza excepción, incluso si ninguna ruta es escribible; en ese caso el logger queda solo con handler de consola.

- [ ] **Step 1: Escribir el test que falla**

Crear `src/test/test_logger_config.py`:

```python
import logging
import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from model.logger_config import setup_logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Evita que los handlers se acumulen entre tests."""
    yield
    logger = logging.getLogger("GestionExpediente")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_setup_logger_returns_logger(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "GestionExpediente"


def test_setup_logger_writes_file_in_writable_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    logger = setup_logger()
    logger.info("mensaje de prueba")

    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert os.path.exists(file_handlers[0].baseFilename)


def test_setup_logger_survives_unwritable_location(monkeypatch):
    """Regresion: no debe lanzar excepcion si no puede crear el archivo.

    Este es el fallo que impedia arrancar desde Program Files.
    """
    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(logging, "FileHandler", deny)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    stream_handlers = [
        h for h in logger.handlers if isinstance(h, logging.StreamHandler)
    ]
    assert len(stream_handlers) >= 1


def test_setup_logger_never_raises_on_makedirs_failure(monkeypatch):
    """Regresion: os.makedirs fallando no debe propagar excepcion."""
    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(os, "makedirs", deny)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
```

- [ ] **Step 2: Ejecutar el test y verificar que falla**

Run: `.venv/Scripts/python.exe -m pytest src/test/test_logger_config.py -v`
Expected: FAIL — `test_setup_logger_never_raises_on_makedirs_failure` propaga `PermissionError`

- [ ] **Step 3: Reescribir `setup_logger`**

Reemplazar el contenido completo de `src/model/logger_config.py`:

```python
from datetime import datetime
import logging
import os
import sys

from utils.resource_manager import resource_manager


def setup_logger():
    """
    Configura el logger principal de la aplicacion.

    El logging nunca debe impedir que la aplicacion arranque: si el
    destino de archivo no es escribible, el logger queda operativo
    solo con salida por consola.
    """
    logger = logging.getLogger("GestionExpediente")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        log_dir = resource_manager.get_writable_path("logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Logging a archivo deshabilitado: {e}")

    return logger
```

- [ ] **Step 4: Ejecutar los tests y verificar que pasan**

Run: `.venv/Scripts/python.exe -m pytest src/test/test_logger_config.py src/test/test_resource_manager.py -v`
Expected: PASS — 8 tests

- [ ] **Step 5: Verificar que la aplicación sigue arrancando en desarrollo**

Run: `.venv/Scripts/python.exe src/__main__.py`
Expected: la ventana de AgilEx abre normalmente. Confirmar que se creó `AgilEx/logs/app_<timestamp>.log` bajo el directorio actual. Cerrar la ventana.

- [ ] **Step 6: Commit**

```bash
git add src/model/logger_config.py src/test/test_logger_config.py
git commit -m "fix: logger usa ruta escribible y nunca bloquea el arranque

log_dir era relativo al CWD, lo que producia PermissionError al
ejecutar desde Program Files e impedia que la aplicacion abriera.
Ahora usa ResourceManager.get_writable_path y degrada a consola si
el archivo no es escribible."
```

---

### Task 3: Eliminar escritura en el árbol de la aplicación

**Files:**
- Modify: `src/view/tools_launcher.py:15-56` (función `create_tool_images`) y el punto donde la ventana carga las imágenes (`src/view/tools_launcher.py:228`)

**Interfaces:**
- Consumes: `ResourceManager.get_path(relative_path)` existente y `ResourceManager.file_exists(relative_path)` existente.
- Produces: ningún símbolo nuevo. `create_tool_images()` deja de invocarse en runtime y queda documentada como utilidad de desarrollo.

- [ ] **Step 1: Localizar dónde se invoca `create_tool_images` y dónde se cargan las imágenes**

Run: `grep -n "create_tool_images\|img_path\|Image.open" src/view/tools_launcher.py`
Expected: muestra la definición (línea ~15), la carga en la línea ~228, y cualquier invocación en runtime.

- [ ] **Step 2: Marcar `create_tool_images` como utilidad de desarrollo**

En `src/view/tools_launcher.py`, sustituir la firma y el docstring de la función (líneas 15-21) por:

```python
def create_tool_images(output_dir="src/assets/tools"):
    """
    UTILIDAD DE DESARROLLO — no invocar en runtime.

    Genera las imagenes de placeholder de las herramientas. Se ejecuta
    manualmente durante el desarrollo; las imagenes resultantes viajan
    en el bundle via config/main.spec. En produccion la aplicacion se
    instala en Program Files, donde escribir en su propio arbol de
    archivos falla con PermissionError.
    """
    os.makedirs(output_dir, exist_ok=True)
```

- [ ] **Step 3: Hacer que la carga de imágenes tolere la ausencia del archivo**

En `src/view/tools_launcher.py`, envolver la carga de la imagen (línea ~228) de modo que un archivo ausente no rompa la ventana. Sustituir la línea `img = Image.open(img_path)` y su contexto inmediato por:

```python
                try:
                    img = Image.open(img_path)
                except (FileNotFoundError, OSError):
                    img = Image.new("RGB", (350, 150), "#4a7aaf")
```

- [ ] **Step 4: Verificar que no queda ninguna invocación en runtime**

Run: `grep -n "create_tool_images()" src/view/tools_launcher.py src/view/application.py src/__main__.py`
Expected: sin resultados. Si aparece alguna llamada, eliminarla.

- [ ] **Step 5: Verificar que la ventana de herramientas abre**

Run: `.venv/Scripts/python.exe src/__main__.py`
Expected: la aplicación abre; la ventana de herramientas muestra las imágenes sin errores en consola. Cerrar.

- [ ] **Step 6: Commit**

```bash
git add src/view/tools_launcher.py
git commit -m "fix: eliminar escritura de imagenes en el arbol de la aplicacion

create_tool_images escribia en src/assets/tools, ruta de solo lectura
tras instalar en Program Files. Queda como utilidad de desarrollo; la
ventana lee del bundle y usa un placeholder en memoria si falta un
archivo."
```

---

### Task 4: Puerta de validación de la Fase A

**Files:**
- Ninguno. Tarea exclusivamente de verificación; no debe modificar código.

**Interfaces:**
- Consumes: los cambios de las Tareas 1-3.
- Produces: evidencia de que el ejecutable empaquetado arranca desde una ruta de solo lectura. **La Fase B no comienza si esta tarea no pasa.**

- [ ] **Step 1: Ejecutar la suite completa de tests**

Run: `.venv/Scripts/python.exe -m pytest src/test/test_resource_manager.py src/test/test_logger_config.py -v`
Expected: PASS — 8 tests

- [ ] **Step 2: Compilar el ejecutable sin firmar**

Run: `.venv/Scripts/pyinstaller.exe config/main.spec --clean`
Expected: se genera `dist/AgilEx_by_Marduk.exe` sin errores.

- [ ] **Step 3: Crear una carpeta de solo lectura y copiar el ejecutable**

```powershell
$dir = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_readonly_test"
New-Item -ItemType Directory -Force -Path $dir | Out-Null
Copy-Item "dist\AgilEx_by_Marduk.exe" $dir
icacls $dir /deny "$env:USERNAME:(WD,AD)"
```

- [ ] **Step 4: Ejecutar desde la carpeta de solo lectura**

```powershell
Start-Process -FilePath "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_readonly_test\AgilEx_by_Marduk.exe" -WorkingDirectory "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_readonly_test"
```

Expected: la ventana de AgilEx **abre**. Antes de la Fase A este escenario fallaba silenciosamente.

- [ ] **Step 5: Verificar la ubicación de los logs**

```powershell
Get-ChildItem "$env:LOCALAPPDATA\AgilEx\logs" | Select-Object -Last 3
```

Expected: al menos un `app_<timestamp>.log` reciente.

- [ ] **Step 6: Validar equivalencia funcional con las tres estrategias**

Procesar un expediente de prueba con cada modo desde la aplicación abierta:
1. Cuaderno único (`selected_value = "1"`)
2. Expediente único (`selected_value = "2"`)
3. Múltiples expedientes (`selected_value = "3"`)

Expected: los tres generan índice Excel correctamente. Comparar el índice resultante contra el producido por la versión 1.5.1 sobre el mismo expediente — deben ser equivalentes en estructura y contenido.

- [ ] **Step 7: Restaurar permisos de la carpeta de prueba**

```powershell
$dir = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_readonly_test"
icacls $dir /remove:d "$env:USERNAME"
Remove-Item -Recurse -Force $dir
```

- [ ] **Step 8: Registrar la evidencia y commitear**

Crear `scripts/certificacion_firma_digital/evidencias/validacion_fase_a.txt` con: fecha de ejecución, resultado de cada paso, ruta de logs confirmada y confirmación de equivalencia de las tres estrategias.

```bash
git add scripts/certificacion_firma_digital/evidencias/validacion_fase_a.txt
git commit -m "test: evidencia de validacion de Fase A

Ejecutable arranca desde carpeta de solo lectura, logs en LOCALAPPDATA
y equivalencia funcional confirmada en las tres estrategias."
```

---

## FASE B — Instalador y pipeline de firma

### Task 5: Definición del instalador WiX

**Files:**
- Create: `installer/wix/Product.wxs`
- Create: `installer/wix/License.rtf`

**Interfaces:**
- Consumes: `dist/AgilEx_by_Marduk.exe` producido por PyInstaller; `src/assets/law_logo.ico`.
- Produces: `Product.wxs` compilable con `wix build`, que acepta las variables de preprocesador `ExeSourcePath` (ruta al `.exe` a empaquetar) y `ProductVersion` (tres campos, ej. `1.5.1`).

- [ ] **Step 1: Instalar WiX v6**

Run: `dotnet tool install --global wix`
Expected: instalación correcta. Verificar con `wix --version`.

Si ya estuviera instalado: `dotnet tool update --global wix`

- [ ] **Step 2: Generar el UpgradeCode definitivo**

Run: `powershell -Command "[guid]::NewGuid().ToString().ToUpper()"`
Expected: un GUID. **Anotarlo** — se usa en el paso siguiente y no vuelve a cambiar nunca.

- [ ] **Step 3: Crear la licencia del instalador**

Crear `installer/wix/License.rtf` con el texto de la licencia MIT del proyecto en formato RTF. Contenido mínimo:

```rtf
{\rtf1\ansi\deff0
{\fonttbl{\f0 Segoe UI;}}
\f0\fs20
AgilEx by Marduk\par
\par
Copyright (c) 2024-2026 Daniel Arbelaez Alvarez\par
\par
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:\par
\par
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\par
\par
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.\par
}
```

- [ ] **Step 4: Crear `Product.wxs`**

Crear `installer/wix/Product.wxs`, sustituyendo `PEGAR-GUID-AQUI` por el GUID del Step 2:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
  AgilEx by Marduk — definicion del instalador MSI

  ADVERTENCIA: el UpgradeCode NO debe modificarse nunca. Es lo que
  permite que las versiones futuras se reconozcan como actualizaciones
  del mismo producto. Cambiarlo rompe la cadena de actualizaciones en
  todos los endpoints ya desplegados.

  Variables de preprocesador requeridas:
    -d ExeSourcePath=<ruta al AgilEx_by_Marduk.exe firmado>
    -d ProductVersion=<version de tres campos, ej. 1.5.1>
-->
<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs"
     xmlns:ui="http://wixtoolset.org/schemas/v4/wxs/ui">

  <Package
      Name="AgilEx by Marduk - Gestión de Expediente Electrónico"
      Manufacturer="Daniel Arbelaez Alvarez"
      Version="$(ProductVersion)"
      UpgradeCode="PEGAR-GUID-AQUI"
      Scope="perMachine"
      Compressed="yes"
      Language="1034"
      Codepage="1252">

    <SummaryInformation
        Description="Automatización RDA para expediente electrónico judicial colombiano (PCSJA20-11567/2020)"
        Manufacturer="Daniel Arbelaez Alvarez" />

    <MajorUpgrade
        Schedule="afterInstallInitialize"
        AllowDowngrades="no"
        DowngradeErrorMessage="Ya está instalada una versión más reciente de AgilEx by Marduk. Desinstálela antes de continuar." />

    <MediaTemplate EmbedCab="yes" />

    <Icon Id="AgilExIcon" SourceFile="..\..\src\assets\law_logo.ico" />
    <Property Id="ARPPRODUCTICON" Value="AgilExIcon" />
    <Property Id="ARPCONTACT" Value="darbelaal@cendoj.ramajudicial.gov.co" />
    <Property Id="ARPURLINFOABOUT" Value="https://github.com/HammerDev99/GestionExpedienteElectronico_Version1" />
    <Property Id="ARPNOMODIFY" Value="1" />

    <StandardDirectory Id="ProgramFiles64Folder">
      <Directory Id="INSTALLFOLDER" Name="AgilEx by Marduk" />
    </StandardDirectory>

    <StandardDirectory Id="ProgramMenuFolder">
      <Directory Id="ApplicationProgramsFolder" Name="AgilEx by Marduk" />
    </StandardDirectory>

    <StandardDirectory Id="DesktopFolder" />

    <ComponentGroup Id="ProductComponents">

      <Component Id="CmpMainExecutable" Directory="INSTALLFOLDER" Guid="*">
        <File Id="FileMainExecutable"
              Source="$(ExeSourcePath)"
              Name="AgilEx_by_Marduk.exe"
              KeyPath="yes" />
      </Component>

      <!--
        Los accesos directos per-machine requieren un KeyPath en HKLM
        para que la validacion ICE del MSI sea correcta. Sin el, wix
        emite advertencias que pueden leerse como paquete mal formado.
      -->
      <Component Id="CmpStartMenuShortcut" Directory="ApplicationProgramsFolder" Guid="*">
        <Shortcut Id="StartMenuShortcut"
                  Name="AgilEx by Marduk"
                  Description="Generador de índices electrónicos de expedientes judiciales"
                  Target="[INSTALLFOLDER]AgilEx_by_Marduk.exe"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="AgilExIcon" />
        <RemoveFolder Id="RemoveApplicationProgramsFolder"
                      Directory="ApplicationProgramsFolder"
                      On="uninstall" />
        <RegistryValue Root="HKLM"
                       Key="Software\AgilEx by Marduk"
                       Name="StartMenuShortcut"
                       Type="integer"
                       Value="1"
                       KeyPath="yes" />
      </Component>

      <Component Id="CmpDesktopShortcut" Directory="DesktopFolder" Guid="*">
        <Shortcut Id="DesktopShortcut"
                  Name="AgilEx by Marduk"
                  Description="Generador de índices electrónicos de expedientes judiciales"
                  Target="[INSTALLFOLDER]AgilEx_by_Marduk.exe"
                  WorkingDirectory="INSTALLFOLDER"
                  Icon="AgilExIcon" />
        <RegistryValue Root="HKLM"
                       Key="Software\AgilEx by Marduk"
                       Name="DesktopShortcut"
                       Type="integer"
                       Value="1"
                       KeyPath="yes" />
      </Component>

    </ComponentGroup>

    <Feature Id="Main" Title="AgilEx by Marduk" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>

    <ui:WixUI Id="WixUI_InstallDir" InstallDirectory="INSTALLFOLDER" />
    <WixVariable Id="WixUILicenseRtf" Value="License.rtf" />

  </Package>
</Wix>
```

- [ ] **Step 5: Compilar el MSI de prueba**

```powershell
wix extension add -g WixToolset.UI.wixext
wix build installer\wix\Product.wxs `
  -ext WixToolset.UI.wixext `
  -d ExeSourcePath="$PWD\dist\AgilEx_by_Marduk.exe" `
  -d ProductVersion="1.5.1" `
  -o "$PWD\dist\AgilEx_test.msi"
```

Expected: `dist\AgilEx_test.msi` generado **sin advertencias ICE**. Si aparecen advertencias, corregirlas antes de continuar.

- [ ] **Step 6: Verificar instalación, accesos directos y desinstalación**

```powershell
Start-Process msiexec -ArgumentList '/i','dist\AgilEx_test.msi','/qn','/l*v','dist\install.log' -Wait
Test-Path "$env:ProgramFiles\AgilEx by Marduk\AgilEx_by_Marduk.exe"
Test-Path "$env:PUBLIC\Desktop\AgilEx by Marduk.lnk"
Test-Path "$env:ProgramData\Microsoft\Windows\Start Menu\Programs\AgilEx by Marduk\AgilEx by Marduk.lnk"
```

Expected: los tres `Test-Path` devuelven `True`.

Abrir la aplicación desde el acceso directo del escritorio. Expected: **la ventana abre** (esto valida la Fase A en condiciones reales).

```powershell
Start-Process msiexec -ArgumentList '/x','dist\AgilEx_test.msi','/qn' -Wait
Test-Path "$env:ProgramFiles\AgilEx by Marduk"
```

Expected: `False` — desinstalación sin residuos.

- [ ] **Step 7: Commit**

```bash
git add installer/wix/Product.wxs installer/wix/License.rtf
git commit -m "feat: definicion WiX del instalador MSI

Instalacion per-machine en Program Files con accesos directos en menu
inicio y escritorio, MajorUpgrade con bloqueo de downgrade y metadatos
ARP consistentes con version_info.rc. El UpgradeCode queda fijo de por
vida."
```

---

### Task 6: Script de firma — preflight e integridad

**Files:**
- Create: `installer/build-signed-msi.ps1` (etapas 0 y 1)

**Interfaces:**
- Consumes: `MANIFIESTO.txt` (generado en la Tarea 8) con el formato `SHA256=<hash>` y `VERSION=<version>`; `bin\AgilEx_by_Marduk.exe`.
- Produces: script con los parámetros `-Thumbprint` (obligatorio), `-TimestampUrl`, `-SkipRar`, `-OutputDir`. Define las funciones `Test-Prerequisites` y `Test-BinaryIntegrity`, y la variable `$script:IsSelfSigned` que consume la Tarea 7. Códigos de salida: 10 (preflight), 20 (integridad).

- [ ] **Step 1: Crear el esqueleto con parámetros y preflight**

Crear `installer/build-signed-msi.ps1`:

```powershell
<#
.SYNOPSIS
    Firma y empaqueta AgilEx by Marduk como MSI distribuible.

.DESCRIPTION
    Ejecuta seis etapas: preflight, verificacion de integridad, firma del
    ejecutable, empaquetado MSI, firma del MSI y compresion RAR. Genera
    REPORTE_FIRMA.txt como evidencia.

    El script no toma decisiones ni corrige errores: valida y se detiene
    con un mensaje accionable ante cualquier anomalia.

.PARAMETER Thumbprint
    Huella del certificado de firma, presente en Cert:\CurrentUser\My o
    Cert:\LocalMachine\My.

.EXAMPLE
    .\build-signed-msi.ps1 -Thumbprint "A1B2C3D4E5F6..."
#>
param(
    [Parameter(Mandatory = $true)]
    [string]$Thumbprint,

    [string]$TimestampUrl = "http://timestamp.digicert.com",
    [string]$OutputDir = "",
    [switch]$SkipRar
)

$ErrorActionPreference = "Stop"
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

$script:Root = $PSScriptRoot
$script:ExePath = Join-Path $script:Root "bin\AgilEx_by_Marduk.exe"
$script:WxsPath = Join-Path $script:Root "wix\Product.wxs"
$script:ManifestPath = Join-Path $script:Root "MANIFIESTO.txt"
$script:IsSelfSigned = $false
$script:SignTool = $null
$script:RarExe = $null

if ($OutputDir -eq "") { $OutputDir = Join-Path $script:Root "salida" }
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
}

$script:TranscriptPath = Join-Path $OutputDir "transcript.log"
Start-Transcript -Path $script:TranscriptPath -Force | Out-Null

function Write-Stage {
    param([string]$Message)
    Write-Host ""
    Write-Host "=== $Message ===" -ForegroundColor Cyan
}

function Stop-WithError {
    param([string]$Message, [string]$Action, [int]$Code)
    Write-Host ""
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    Write-Host "[ACCION] $Action" -ForegroundColor Yellow
    Stop-Transcript | Out-Null
    exit $Code
}

function Find-SignTool {
    $base = "${env:ProgramFiles(x86)}\Windows Kits\10\bin"
    if (-not (Test-Path $base)) { return $null }
    $found = Get-ChildItem $base -Recurse -Filter "signtool.exe" -ErrorAction SilentlyContinue |
        Where-Object { $_.FullName -match "\\x64\\" } |
        Sort-Object FullName -Descending |
        Select-Object -First 1
    if ($found) { return $found.FullName }
    return $null
}

function Find-Rar {
    $candidates = @(
        "$env:ProgramFiles\WinRAR\Rar.exe",
        "${env:ProgramFiles(x86)}\WinRAR\Rar.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

function Test-Prerequisites {
    Write-Stage "Etapa 0/6 - Preflight"

    $script:SignTool = Find-SignTool
    if (-not $script:SignTool) {
        Stop-WithError -Message "No se encontro signtool.exe" `
            -Action "Instale el Windows SDK (componente Signing Tools)." -Code 10
    }
    Write-Host "[OK] signtool: $($script:SignTool)" -ForegroundColor Green

    $wix = Get-Command wix -ErrorAction SilentlyContinue
    if (-not $wix) {
        Stop-WithError -Message "No se encontro la herramienta wix" `
            -Action "Ejecute: dotnet tool install --global wix" -Code 10
    }
    Write-Host "[OK] wix: $($wix.Source)" -ForegroundColor Green

    $script:RarExe = Find-Rar
    if (-not $script:RarExe -and -not $SkipRar) {
        Write-Host "[AVISO] Rar.exe no encontrado. La etapa 5 se omitira." -ForegroundColor Yellow
    }

    if (-not (Test-Path $script:ExePath)) {
        Stop-WithError -Message "No se encontro bin\AgilEx_by_Marduk.exe" `
            -Action "Verifique que descomprimio el paquete completo." -Code 10
    }

    if (-not (Test-Path $script:ManifestPath)) {
        Stop-WithError -Message "No se encontro MANIFIESTO.txt" `
            -Action "Verifique que descomprimio el paquete completo." -Code 10
    }

    $cert = Get-ChildItem -Path Cert:\CurrentUser\My, Cert:\LocalMachine\My -ErrorAction SilentlyContinue |
        Where-Object { $_.Thumbprint -eq $Thumbprint } |
        Select-Object -First 1

    if (-not $cert) {
        Stop-WithError -Message "No se encontro el certificado $Thumbprint" `
            -Action "Verifique la huella con: Get-ChildItem Cert:\CurrentUser\My" -Code 10
    }

    if ($cert.NotAfter -lt (Get-Date)) {
        Stop-WithError -Message "El certificado vencio el $($cert.NotAfter)" `
            -Action "Use un certificado vigente." -Code 10
    }

    $hasCodeSigning = $cert.Extensions |
        Where-Object { $_.Oid.FriendlyName -eq "Enhanced Key Usage" } |
        ForEach-Object { $_.Format($false) } |
        Where-Object { $_ -match "Code Signing|1\.3\.6\.1\.5\.5\.7\.3\.3" }

    if (-not $hasCodeSigning) {
        Stop-WithError -Message "El certificado no tiene EKU Code Signing" `
            -Action "Use un certificado emitido para firma de codigo." -Code 10
    }

    $script:IsSelfSigned = ($cert.Subject -eq $cert.Issuer)

    Write-Host "[OK] Certificado: $($cert.Subject)" -ForegroundColor Green
    Write-Host "     Vigencia hasta: $($cert.NotAfter)" -ForegroundColor Gray
    if ($script:IsSelfSigned) {
        Write-Host "[AVISO] Certificado autofirmado: modo de prueba." -ForegroundColor Yellow
    }

    return $cert
}

function Test-BinaryIntegrity {
    Write-Stage "Etapa 1/6 - Verificacion de integridad"

    $declared = (Get-Content $script:ManifestPath |
        Where-Object { $_ -match "^SHA256=" }) -replace "^SHA256=", ""
    $declared = $declared.Trim().ToUpper()

    if (-not $declared) {
        Stop-WithError -Message "MANIFIESTO.txt no declara SHA256" `
            -Action "Solicite al desarrollador un paquete valido." -Code 20
    }

    $actual = (Get-FileHash $script:ExePath -Algorithm SHA256).Hash.ToUpper()

    if ($actual -ne $declared) {
        Stop-WithError -Message "El SHA256 del ejecutable no coincide con el declarado.`n  Esperado: $declared`n  Obtenido: $actual" `
            -Action "NO FIRMAR. El binario fue alterado en transito. Solicite reenvio." -Code 20
    }

    Write-Host "[OK] SHA256 verificado: $actual" -ForegroundColor Green
    return $actual
}
```

- [ ] **Step 2: Añadir el bloque principal provisional para probar las dos etapas**

Añadir al final de `installer/build-signed-msi.ps1`:

```powershell
# ----- Bloque principal -----
$cert = Test-Prerequisites
$hashBefore = Test-BinaryIntegrity

Write-Host ""
Write-Host "Etapas 0 y 1 completadas." -ForegroundColor Green
Stop-Transcript | Out-Null
```

- [ ] **Step 3: Preparar una carpeta de prueba del paquete**

```powershell
$pkg = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test"
New-Item -ItemType Directory -Force -Path "$pkg\bin","$pkg\wix" | Out-Null
Copy-Item "dist\AgilEx_by_Marduk.exe" "$pkg\bin\"
Copy-Item "installer\wix\*" "$pkg\wix\"
Copy-Item "installer\build-signed-msi.ps1" $pkg
$h = (Get-FileHash "$pkg\bin\AgilEx_by_Marduk.exe" -Algorithm SHA256).Hash
Set-Content "$pkg\MANIFIESTO.txt" "SHA256=$h`nVERSION=1.5.1"
```

- [ ] **Step 4: Ejecutar y verificar que ambas etapas pasan**

```powershell
& "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test\build-signed-msi.ps1" -Thumbprint "92ADA07AA3455816E2555C6CDF8D5120AE7D57B1"
```

Expected: `[OK] signtool`, `[OK] wix`, `[OK] Certificado`, `[AVISO] Certificado autofirmado`, `[OK] SHA256 verificado`, y "Etapas 0 y 1 completadas".

- [ ] **Step 5: Verificar que la integridad alterada aborta con código 20**

```powershell
$pkg = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test"
Set-Content "$pkg\MANIFIESTO.txt" "SHA256=0000000000000000000000000000000000000000000000000000000000000000`nVERSION=1.5.1"
& "$pkg\build-signed-msi.ps1" -Thumbprint "92ADA07AA3455816E2555C6CDF8D5120AE7D57B1"
$LASTEXITCODE
```

Expected: mensaje "NO FIRMAR. El binario fue alterado en transito" y `$LASTEXITCODE` igual a `20`.

Restaurar el manifiesto correcto antes de continuar:

```powershell
$h = (Get-FileHash "$pkg\bin\AgilEx_by_Marduk.exe" -Algorithm SHA256).Hash
Set-Content "$pkg\MANIFIESTO.txt" "SHA256=$h`nVERSION=1.5.1"
```

- [ ] **Step 6: Commit**

```bash
git add installer/build-signed-msi.ps1
git commit -m "feat: script de firma - etapas de preflight e integridad

Valida signtool, wix, Rar.exe y el certificado (vigencia, EKU Code
Signing, autofirmado o no) y verifica el SHA256 del ejecutable contra
MANIFIESTO.txt antes de firmar. Codigos de salida 10 y 20."
```

---

### Task 7: Script de firma — firma, empaquetado, compresión y reporte

**Files:**
- Modify: `installer/build-signed-msi.ps1` (añadir etapas 2-6 y sustituir el bloque principal provisional)

**Interfaces:**
- Consumes: `Test-Prerequisites`, `Test-BinaryIntegrity`, `$script:SignTool`, `$script:RarExe`, `$script:IsSelfSigned`, `Stop-WithError`, `Write-Stage` de la Tarea 6.
- Produces: `<OutputDir>\AgilEx_by_Marduk_v<version>_firmado.msi`, `<OutputDir>\AgilEx_v<version>_firmado.rar` y `<OutputDir>\REPORTE_FIRMA.txt`. Códigos de salida: 30 (firma exe), 40 (MSI), 50 (firma MSI).

- [ ] **Step 1: Añadir las funciones de firma y empaquetado**

Insertar en `installer/build-signed-msi.ps1`, **antes** del comentario `# ----- Bloque principal -----`:

```powershell
function Invoke-SignFile {
    param(
        [string]$Path,
        [string]$Description,
        [int]$ErrorCode
    )

    $args = @(
        "sign",
        "/sha1", $Thumbprint,
        "/fd", "SHA256",
        "/td", "SHA256",
        "/tr", $TimestampUrl,
        "/d", "AgilEx by Marduk",
        $Path
    )

    & $script:SignTool @args
    if ($LASTEXITCODE -ne 0) {
        Stop-WithError -Message "signtool fallo al firmar $Description (exit $LASTEXITCODE)" `
            -Action "Verifique la conectividad con $TimestampUrl y los permisos del certificado." -Code $ErrorCode
    }

    $sig = Get-AuthenticodeSignature $Path

    if ($sig.Status -eq "Valid") {
        Write-Host "[OK] Firma valida en $Description" -ForegroundColor Green
    }
    elseif ($sig.Status -eq "UnknownError" -and $script:IsSelfSigned) {
        Write-Host "[AVISO] Firma integra pero la cadena no encadena a una raiz de confianza." -ForegroundColor Yellow
        Write-Host "        Esperado con certificado autofirmado (modo de prueba)." -ForegroundColor Yellow
    }
    else {
        Stop-WithError -Message "Estado de firma inesperado en ${Description}: $($sig.Status)" `
            -Action "Revise el certificado y vuelva a intentarlo." -Code $ErrorCode
    }

    return $sig
}

function Get-ProductVersion {
    $declared = (Get-Content $script:ManifestPath |
        Where-Object { $_ -match "^VERSION=" }) -replace "^VERSION=", ""
    $declared = $declared.Trim()
    if (-not $declared) {
        Stop-WithError -Message "MANIFIESTO.txt no declara VERSION" `
            -Action "Solicite al desarrollador un paquete valido." -Code 40
    }
    return $declared
}

function Build-Msi {
    param([string]$Version, [string]$Destination)

    Write-Stage "Etapa 3/6 - Empaquetado MSI"

    & wix extension add -g WixToolset.UI.wixext 2>&1 | Out-Null

    & wix build $script:WxsPath `
        -ext WixToolset.UI.wixext `
        -d ExeSourcePath="$script:ExePath" `
        -d ProductVersion="$Version" `
        -o $Destination

    if ($LASTEXITCODE -ne 0) {
        Stop-WithError -Message "wix build fallo (exit $LASTEXITCODE)" `
            -Action "Revise el transcript en $script:TranscriptPath" -Code 40
    }

    Write-Host "[OK] MSI generado: $Destination" -ForegroundColor Green
}

function Compress-Package {
    param([string]$MsiPath, [string]$RarPath)

    Write-Stage "Etapa 5/6 - Compresion RAR"

    if ($SkipRar) {
        Write-Host "[OMITIDO] -SkipRar activo" -ForegroundColor Yellow
        return $false
    }
    if (-not $script:RarExe) {
        Write-Host "[OMITIDO] Rar.exe no disponible. El MSI firmado queda en $MsiPath" -ForegroundColor Yellow
        return $false
    }

    & $script:RarExe a -m5 -ep1 $RarPath $MsiPath | Out-Null

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $RarPath)) {
        Write-Host "[AVISO] La compresion fallo. El MSI firmado sigue siendo valido." -ForegroundColor Yellow
        return $false
    }

    Write-Host "[OK] RAR generado: $RarPath" -ForegroundColor Green
    return $true
}

function Write-SignatureReport {
    param(
        [string]$ReportPath,
        $Certificate,
        [string]$Version,
        [string]$ExeHashBefore,
        [string]$ExeHashAfter,
        [string]$MsiPath,
        [string]$MsiHash,
        [bool]$RarCreated
    )

    $exeSig = Get-AuthenticodeSignature $script:ExePath
    $msiSig = Get-AuthenticodeSignature $MsiPath

    $lines = @(
        "REPORTE DE FIRMA - AgilEx by Marduk",
        "===================================",
        "",
        "Fecha de ejecucion : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "Equipo             : $env:COMPUTERNAME",
        "Version del producto: $Version",
        "",
        "CERTIFICADO",
        "-----------",
        "Subject    : $($Certificate.Subject)",
        "Issuer     : $($Certificate.Issuer)",
        "Thumbprint : $($Certificate.Thumbprint)",
        "Vigencia   : $($Certificate.NotBefore) a $($Certificate.NotAfter)",
        "Autofirmado: $($script:IsSelfSigned)",
        "Timestamp  : $TimestampUrl",
        "",
        "EJECUTABLE",
        "----------",
        "SHA256 antes de firmar : $ExeHashBefore",
        "SHA256 despues de firmar: $ExeHashAfter",
        "Estado de firma        : $($exeSig.Status)",
        "",
        "INSTALADOR MSI",
        "--------------",
        "Archivo         : $(Split-Path $MsiPath -Leaf)",
        "SHA256          : $MsiHash",
        "Estado de firma : $($msiSig.Status)",
        "",
        "DISTRIBUCION",
        "------------",
        "RAR generado : $RarCreated",
        "",
        "NOTA SOBRE TRAZABILIDAD",
        "-----------------------",
        "El SHA256 del ejecutable cambia al firmarlo. Si se compara contra",
        "el hash documentado ante el SOC para el binario sin firma",
        "institucional, la diferencia es esperada y no indica alteracion.",
        "Incidente relacionado: RJ-MDE-MAL-ALERT-002 / ID 804977."
    )

    $lines | Set-Content -Path $ReportPath -Encoding UTF8
    Write-Host "[OK] Reporte generado: $ReportPath" -ForegroundColor Green
}
```

- [ ] **Step 2: Sustituir el bloque principal provisional por el definitivo**

Reemplazar en `installer/build-signed-msi.ps1` el bloque que empieza en `# ----- Bloque principal -----` por:

```powershell
# ----- Bloque principal -----
$cert = Test-Prerequisites
$hashBefore = Test-BinaryIntegrity

Write-Stage "Etapa 2/6 - Firma del ejecutable"
Invoke-SignFile -Path $script:ExePath -Description "el ejecutable" -ErrorCode 30 | Out-Null
$hashAfter = (Get-FileHash $script:ExePath -Algorithm SHA256).Hash.ToUpper()

$version = Get-ProductVersion
$msiName = "AgilEx_by_Marduk_v${version}_firmado.msi"
$msiPath = Join-Path $OutputDir $msiName
Build-Msi -Version $version -Destination $msiPath

Write-Stage "Etapa 4/6 - Firma del MSI"
Invoke-SignFile -Path $msiPath -Description "el MSI" -ErrorCode 50 | Out-Null
$msiHash = (Get-FileHash $msiPath -Algorithm SHA256).Hash.ToUpper()

$rarPath = Join-Path $OutputDir "AgilEx_v${version}_firmado.rar"
$rarCreated = Compress-Package -MsiPath $msiPath -RarPath $rarPath

Write-Stage "Etapa 6/6 - Reporte de evidencia"
$reportPath = Join-Path $OutputDir "REPORTE_FIRMA.txt"
Write-SignatureReport -ReportPath $reportPath -Certificate $cert -Version $version `
    -ExeHashBefore $hashBefore -ExeHashAfter $hashAfter `
    -MsiPath $msiPath -MsiHash $msiHash -RarCreated $rarCreated

Write-Host ""
Write-Host "===========================================" -ForegroundColor Green
Write-Host " Proceso completado" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
Write-Host " Salida: $OutputDir" -ForegroundColor Gray
Write-Host ""

Stop-Transcript | Out-Null
exit 0
```

- [ ] **Step 3: Sincronizar el script en la carpeta de prueba y ejecutarlo completo**

```powershell
$pkg = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test"
Copy-Item "installer\build-signed-msi.ps1" $pkg -Force
$h = (Get-FileHash "$pkg\bin\AgilEx_by_Marduk.exe" -Algorithm SHA256).Hash
Set-Content "$pkg\MANIFIESTO.txt" "SHA256=$h`nVERSION=1.5.1"
& "$pkg\build-signed-msi.ps1" -Thumbprint "92ADA07AA3455816E2555C6CDF8D5120AE7D57B1"
$LASTEXITCODE
```

Expected: las seis etapas completan, `$LASTEXITCODE` es `0`, y en `$pkg\salida\` aparecen el `.msi` firmado, el `.rar` y `REPORTE_FIRMA.txt`. Los avisos de firma autofirmada son esperados.

- [ ] **Step 4: Verificar el contenido del reporte**

```powershell
Get-Content "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test\salida\REPORTE_FIRMA.txt"
```

Expected: hashes antes y después distintos entre sí, datos del certificado, ambos estados de firma y la nota de trazabilidad.

- [ ] **Step 5: Verificar que el MSI firmado instala y la app abre**

```powershell
$pkg = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test"
$msi = Get-ChildItem "$pkg\salida\*.msi" | Select-Object -First 1
Start-Process msiexec -ArgumentList '/i',"`"$($msi.FullName)`"",'/qn','/l*v',"$pkg\install.log" -Wait
Test-Path "$env:ProgramFiles\AgilEx by Marduk\AgilEx_by_Marduk.exe"
```

Expected: `True`. Abrir desde el acceso directo del escritorio y confirmar que la ventana abre. Luego desinstalar:

```powershell
Start-Process msiexec -ArgumentList '/x',"`"$($msi.FullName)`"",'/qn' -Wait
```

- [ ] **Step 6: Commit**

```bash
git add installer/build-signed-msi.ps1
git commit -m "feat: script de firma - etapas de firma, MSI, RAR y reporte

Firma el exe, empaqueta el MSI con wix, firma el MSI y comprime en RAR.
La compresion no es fatal si falta Rar.exe. Acepta UnknownError solo
con certificado autofirmado. Genera REPORTE_FIRMA.txt como evidencia."
```

---

### Task 8: Paquete de entrega y documentación

**Files:**
- Create: `scripts/new-delivery-package.ps1`
- Create: `installer/README_SEGURIDAD.md`

**Interfaces:**
- Consumes: `dist/AgilEx_by_Marduk.exe`, `installer/wix/`, `installer/build-signed-msi.ps1`, `src/assets/version_info.rc`.
- Produces: `dist/AgilEx_v<version>_paquete_firma.zip` con la estructura `bin/`, `wix/`, `build-signed-msi.ps1`, `MANIFIESTO.txt`, `README_SEGURIDAD.md`.

- [ ] **Step 1: Crear el README para el área de Seguridad Informática**

Crear `installer/README_SEGURIDAD.md`:

```markdown
# AgilEx by Marduk — Instrucciones de firma y empaquetado

## Qué es este paquete

AgilEx by Marduk es una herramienta de automatización que genera índices electrónicos de expedientes judiciales conforme al Acuerdo PCSJA20-11567 de 2020. Lleva 3.5 años en operación en la Rama Judicial.

Este paquete contiene el ejecutable **sin firmar** junto con las herramientas para que el área de Seguridad Informática lo firme con el certificado institucional, lo empaquete como MSI y lo prepare para distribución.

## Por qué se firman dos archivos

| Artefacto | Qué protege |
|---|---|
| `AgilEx_by_Marduk.exe` | El uso diario. Es el archivo que se ejecuta cada vez que un funcionario abre la aplicación, y el que evalúan Defender/ASR/AppLocker |
| `AgilEx_..._firmado.msi` | La instalación. Es lo que se distribuye y se despliega por GPO/SCCM |

El orden es obligatorio: primero el `.exe`, luego el `.msi`. Un MSI firmado es inmutable, por lo que su contenido debe estar firmado antes de empaquetarlo.

## Prerequisitos

| Herramienta | Cómo instalarla |
|---|---|
| Windows SDK (signtool) | Componente "Signing Tools" del Windows SDK |
| WiX Toolset v6 | `dotnet tool install --global wix` |
| WinRAR | Opcional. Si falta, el proceso deja el MSI firmado sin comprimir |

Se necesita el certificado de firma de código institucional instalado en `Cert:\CurrentUser\My` o `Cert:\LocalMachine\My`.

## Ejecución

1. Descomprimir el paquete completo en una carpeta local.
2. Obtener la huella del certificado:

   ```powershell
   Get-ChildItem Cert:\CurrentUser\My | Format-List Subject, Thumbprint, NotAfter
   ```

3. Ejecutar:

   ```powershell
   .\build-signed-msi.ps1 -Thumbprint "HUELLA_DEL_CERTIFICADO"
   ```

El script no requiere privilegios de administrador ni accede a internet salvo al servicio de sellado de tiempo (`http://timestamp.digicert.com`, configurable con `-TimestampUrl`).

## Qué hace, paso a paso

| Etapa | Acción |
|---|---|
| 0 | Verifica herramientas y certificado (vigencia y EKU de firma de código) |
| 1 | Compara el SHA256 del ejecutable con el declarado en `MANIFIESTO.txt` |
| 2 | Firma el ejecutable con SHA256 y sellado de tiempo RFC 3161 |
| 3 | Empaqueta el MSI con WiX |
| 4 | Firma el MSI |
| 5 | Comprime el MSI en RAR |
| 6 | Genera `REPORTE_FIRMA.txt` |

La etapa 1 permite confirmar que se está firmando exactamente el binario que el desarrollador declaró, sin alteraciones en tránsito.

## Salida

Todo queda en la subcarpeta `salida\`:

- `AgilEx_by_Marduk_v<version>_firmado.msi` — instalador firmado
- `AgilEx_v<version>_firmado.rar` — comprimido para distribución
- `REPORTE_FIRMA.txt` — evidencia con hashes, certificado y sellos de tiempo
- `transcript.log` — traza completa de la ejecución

## Códigos de error

| Código | Etapa | Significado |
|---|---|---|
| 10 | Preflight | Falta una herramienta, o el certificado no existe, está vencido o no sirve para firma de código |
| 20 | Integridad | El SHA256 no coincide. **No firmar**: solicitar reenvío del paquete |
| 30 | Firma exe | `signtool` falló o el estado de la firma es inesperado |
| 40 | MSI | `wix build` falló |
| 50 | Firma MSI | `signtool` falló sobre el MSI |

Ante cualquier fallo, `salida\transcript.log` contiene la traza completa para diagnóstico.

## Nota sobre el hash y el incidente 804977

Este trabajo responde al incidente `RJ-MDE-MAL-ALERT-002` / ID `804977`, en el que Microsoft XDR marcó el ejecutable como `Malgent`.

**El SHA256 del ejecutable cambia al firmarlo.** El hash documentado previamente ante el SOC corresponde al binario firmado con el certificado autofirmado del desarrollador. Tras la firma institucional será distinto, y esa diferencia es esperada — no indica alteración. `REPORTE_FIRMA.txt` registra ambos valores.

Una vez firmado con el certificado institucional, es posible crear una regla de AppLocker/WDAC **por publisher** que confíe en ese certificado. Una sola regla cubre esta versión y todas las futuras sin intervención adicional.

## Contacto

Daniel Arbeláez Álvarez — darbelaal@cendoj.ramajudicial.gov.co
```

- [ ] **Step 2: Crear el generador del paquete de entrega**

Crear `scripts/new-delivery-package.ps1`:

```powershell
<#
.SYNOPSIS
    Genera el paquete de entrega para el area de Seguridad Informatica.

.DESCRIPTION
    Empaqueta el ejecutable sin firmar, los fuentes WiX, el script de
    firma y el MANIFIESTO.txt con el SHA256 declarado.
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
```

- [ ] **Step 3: Generar el paquete y verificar su contenido**

```powershell
.\scripts\new-delivery-package.ps1
$zip = Get-ChildItem "dist\AgilEx_v*_paquete_firma.zip" | Select-Object -First 1
Add-Type -AssemblyName System.IO.Compression.FileSystem
[IO.Compression.ZipFile]::OpenRead($zip.FullName).Entries | Select-Object FullName
```

Expected: el ZIP contiene `bin/AgilEx_by_Marduk.exe`, `wix/Product.wxs`, `wix/License.rtf`, `build-signed-msi.ps1`, `MANIFIESTO.txt` y `README_SEGURIDAD.md`.

- [ ] **Step 4: Prueba de extremo a extremo desde el ZIP**

```powershell
$dest = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_e2e"
if (Test-Path $dest) { Remove-Item -Recurse -Force $dest }
$zip = Get-ChildItem "dist\AgilEx_v*_paquete_firma.zip" | Select-Object -First 1
Expand-Archive $zip.FullName -DestinationPath $dest
& "$dest\build-signed-msi.ps1" -Thumbprint "92ADA07AA3455816E2555C6CDF8D5120AE7D57B1"
$LASTEXITCODE
```

Expected: `$LASTEXITCODE` es `0`. Esto simula exactamente lo que hará el área de Seguridad Informática.

- [ ] **Step 5: Validar la actualización entre versiones (UpgradeCode)**

```powershell
$dest = "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_e2e"
$msi = Get-ChildItem "$dest\salida\*.msi" | Select-Object -First 1
Start-Process msiexec -ArgumentList '/i',"`"$($msi.FullName)`"",'/qn' -Wait

# Regenerar como 1.5.2 y comprobar que actualiza en lugar de duplicar
(Get-Content "$dest\MANIFIESTO.txt") -replace "VERSION=1.5.1","VERSION=1.5.2" |
    Set-Content "$dest\MANIFIESTO.txt"
& "$dest\build-signed-msi.ps1" -Thumbprint "92ADA07AA3455816E2555C6CDF8D5120AE7D57B1"
$msi2 = Get-ChildItem "$dest\salida\*1.5.2*.msi" | Select-Object -First 1
Start-Process msiexec -ArgumentList '/i',"`"$($msi2.FullName)`"",'/qn' -Wait

Get-ItemProperty HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Where-Object { $_.DisplayName -like "*AgilEx*" } |
    Select-Object DisplayName, DisplayVersion
```

Expected: **una sola entrada**, con `DisplayVersion` `1.5.2`. Dos entradas indicarían un `UpgradeCode` mal configurado.

Desinstalar y limpiar:

```powershell
Start-Process msiexec -ArgumentList '/x',"`"$($msi2.FullName)`"",'/qn' -Wait
Remove-Item -Recurse -Force "C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_e2e","C:\Users\$env:USERNAME\AppData\Local\Temp\agilex_pkg_test" -ErrorAction SilentlyContinue
```

- [ ] **Step 6: Registrar evidencia y commitear**

Crear `scripts/certificacion_firma_digital/evidencias/validacion_pipeline_msi.txt` con: fecha, resultado de la prueba de extremo a extremo, confirmación de la actualización 1.5.1 → 1.5.2 con una sola entrada en ARP, y la ruta del `REPORTE_FIRMA.txt` generado.

```bash
git add scripts/new-delivery-package.ps1 installer/README_SEGURIDAD.md scripts/certificacion_firma_digital/evidencias/validacion_pipeline_msi.txt
git commit -m "feat: generador del paquete de entrega y guia para Seguridad Informatica

new-delivery-package.ps1 empaqueta exe, fuentes WiX, script de firma y
MANIFIESTO.txt con el SHA256 declarado. README_SEGURIDAD.md documenta
prerequisitos, ejecucion, codigos de error y la nota de trazabilidad
del hash frente al incidente 804977."
```

---

### Task 9: Documentación del proyecto y bitácora de certificación

**Files:**
- Modify: `scripts/certificacion_firma_digital/README.md` (tabla de control de versiones, sección 4)
- Modify: `CLAUDE.md` (sección de comandos de build)

**Interfaces:**
- Consumes: los artefactos de las Tareas 5-8.
- Produces: ningún símbolo de código. Cierra la trazabilidad documental de la gestión.

- [ ] **Step 1: Añadir el registro a la bitácora de certificación**

En `scripts/certificacion_firma_digital/README.md`, añadir al final de la tabla de la sección 4 ("Control de versiones de la gestión"):

```markdown
| 2026-09-04 | Diseño y construcción del pipeline de empaquetado MSI + firma institucional. Decisión: el área de Seguridad Informática firma `.exe` y `.msi` con certificado institucional; **certificado EV de Andes SCD descartado** en consecuencia. Corrección previa de rutas de escritura que impedían el arranque desde `Program Files` | Daniel Arbeláez + Claude | `docs/superpowers/specs/2026-09-04-msi-pipeline-firma-institucional-design.md`, `installer/`, `evidencias/validacion_fase_a.txt`, `evidencias/validacion_pipeline_msi.txt` |
```

- [ ] **Step 2: Registrar el descarte del EV en la sección de fases**

En el mismo archivo, bajo "### Fase 2 — Certificado EV definitivo", añadir al inicio de la sección:

```markdown
> **Estado 2026-09-04 — DESCARTADO.** El área de Seguridad Informática de la
> Unidad de Transformación Digital firmará los artefactos con el certificado
> institucional de la entidad. La adquisición de un certificado EV propio deja
> de ser necesaria. Ver `docs/superpowers/specs/2026-09-04-msi-pipeline-firma-institucional-design.md` (decisiones D2 y D3).
```

- [ ] **Step 3: Documentar los comandos nuevos en CLAUDE.md**

En `CLAUDE.md`, dentro de la sección "### Build y Empaquetado", añadir después del bloque existente:

````markdown
### Paquete de entrega para firma institucional

```bash
# 1. Compilar el ejecutable (sin firmar)
pyinstaller config/main.spec --clean

# 2. Generar el paquete de entrega para Seguridad Informática
powershell -File scripts/new-delivery-package.ps1
# Produce: dist/AgilEx_v<version>_paquete_firma.zip
```

El área de Seguridad Informática ejecuta `build-signed-msi.ps1` dentro de ese paquete: firma el `.exe`, empaqueta el MSI, lo firma y lo comprime. Ver `installer/README_SEGURIDAD.md`.

**Regla de versionado MSI**: todo release distribuido debe incrementar alguno de los tres primeros campos de la versión (`1.5.1` → `1.5.2`). Un cuarto campo (`1.5.1.1`) es invisible para el motor de actualización de Windows Installer.
````

- [ ] **Step 4: Verificar que la documentación es coherente**

Run: `grep -n "Andes SCD\|EV Code Signing" scripts/certificacion_firma_digital/README.md`
Expected: las menciones al EV aparecen con la nota de descarte del Step 2. Si alguna sección sigue presentando el EV como pendiente sin la advertencia, actualizarla.

- [ ] **Step 5: Commit**

```bash
git add scripts/certificacion_firma_digital/README.md CLAUDE.md
git commit -m "docs: registrar pipeline MSI en bitacora y comandos de build

Anade el hito del 2026-09-04 a la bitacora de certificacion, marca el
certificado EV de Andes SCD como descartado y documenta el flujo de
generacion del paquete de entrega junto con la regla de versionado MSI."
```

---

## Autorrevisión del plan

**Cobertura del spec:**

| Sección del spec | Tarea |
|---|---|
| §3 Arquitectura y frontera | 6, 7, 8 |
| §3.3 Nota de trazabilidad del hash | 7 (reporte), 8 (README) |
| §4.1/4.2 Bloqueante 1 (logger) | 1, 2 |
| §4.2 Bloqueante 2 (tools_launcher) | 3 |
| §4.3 Alcance de no modificación | Global Constraints |
| §5.1 Identidad y UpgradeCode | 5 |
| §5.2 Actualización y versionado | 5, 8 (Step 5) |
| §5.3 Componentes | 5 |
| §5.4 Metadatos ARP | 5 |
| §5.5 Instalación silenciosa | 5 (Step 6), 8 (Step 5) |
| §5.6 Comportamientos excluidos | 5 (nada añadido) |
| §6.1-6.3 Etapas del script | 6, 7 |
| §6.4 Tolerancia RAR | 7 (`Compress-Package`) |
| §6.5 Estados de firma | 6 (detección), 7 (`Invoke-SignFile`) |
| §6.6 Restricciones de comportamiento | 6, 7 |
| §6.7 Evidencia | 7 (`Write-SignatureReport`) |
| §6.8 README_SEGURIDAD | 8 |
| §7.1 Nivel unitario | 1, 2 |
| §7.2 Nivel integración | 4 |
| §7.3 Nivel instalador | 5 (Step 6), 8 (Step 5) |
| §7.4 Validación con autofirmado | 6, 7, 8 |
| §8 Despliegue | 9 (bitácora); ejecución fuera del plan |

**Consistencia de nombres verificada:** `get_writable_path(subdir="")` se define en la Tarea 1 y se consume con el mismo nombre en la Tarea 2. `Test-Prerequisites`, `Test-BinaryIntegrity`, `Stop-WithError`, `Write-Stage`, `$script:SignTool`, `$script:RarExe` y `$script:IsSelfSigned` se definen en la Tarea 6 y se usan idénticos en la Tarea 7. `ExeSourcePath` y `ProductVersion` son coherentes entre el `.wxs` (Tarea 5) y `Build-Msi` (Tarea 7). `MANIFIESTO.txt` usa `SHA256=` y `VERSION=` en las Tareas 6, 7 y 8.

**Nota sobre la Tarea 8, Step 5:** regenera el MSI declarando `VERSION=1.5.2` en el manifiesto sin recompilar el ejecutable. Es deliberado — valida el `UpgradeCode` sin un rebuild completo. La versión del `.exe` seguirá siendo 1.5.1 internamente; para un release real se incrementa `version_info.rc` y se recompila.
