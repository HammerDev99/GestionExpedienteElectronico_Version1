# Guía de Instalación

## Requisitos del Sistema

### Requisitos Obligatorios

#### Microsoft Excel
!!! warning "Requisito Crítico"
    **Microsoft Excel** debe estar instalado en el sistema para el funcionamiento correcto de la aplicación. La aplicación utiliza xlwings para automatización COM, que requiere una instalación completa de Excel.

#### Python
- **Versión**: Python 3.9.6 o superior
- **Arquitectura**: Recomendado 64 bits
- **Origen**: [Descargar desde python.org](https://www.python.org/downloads/)

#### Sistema Operativo
- **Principal**: Windows 10/11 (recomendado)
- **Alternativo**: Windows 7/8 (compatibilidad limitada)
- **Linux/macOS**: Funcionalidad parcial (sin soporte completo de Excel)

### Requisitos Recomendados

#### Hardware
- **RAM**: Mínimo 4GB, recomendado 8GB+
- **Almacenamiento**: 500MB libres para instalación
- **Procesador**: Intel Core i3 o equivalente

#### Software Adicional
- **Git**: Para clonación del repositorio
- **Editor de Texto**: VS Code, PyCharm, etc. (para desarrollo)

## Métodos de Instalación

### Opción 1: Instalación desde Código Fuente (Recomendada)

#### 1. Clonar el Repositorio

```bash
# Clonar repositorio principal
git clone https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git

# Navegar al directorio
cd GestionExpedienteElectronico_Version1
```

#### 2. Configurar Ambiente Virtual

```bash
# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual
# En Windows:
.venv\Scripts\Activate

# En Linux/macOS:
source .venv/bin/activate
```

!!! tip "Buenas Prácticas"
    Siempre utiliza un ambiente virtual para evitar conflictos entre dependencias de diferentes proyectos.

#### 3. Instalar Dependencias

```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias desde requirements.txt
pip install --upgrade -r requirements.txt
```

#### 4. Verificar Instalación

```bash
# Ejecutar la aplicación
python src/__main__.py
```

### Opción 2: Instalación desde Release Pre-compilado

#### 1. Descargar Ejecutable

1. Visita la [página de releases](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases)
2. Descarga la última versión: `AgilEx_by_Marduk.exe`
3. Ejecuta directamente el archivo

!!! note "Ventajas del Ejecutable"
    - No requiere instalación de Python
    - No necesita configuración de dependencias
    - Listo para usar inmediatamente

### Opción 3: Fork Personal (Para Desarrolladores)

#### 1. Crear Fork en GitHub

1. Visita el [repositorio original](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1)
2. Haz clic en "Fork" en la esquina superior derecha
3. Clona tu fork personal:

```bash
git clone https://github.com/TU-USUARIO/GestionExpedienteElectronico_Version1.git
cd GestionExpedienteElectronico_Version1
```

#### 2. Configurar Remotos

```bash
# Agregar repositorio original como upstream
git remote add upstream https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git

# Verificar configuración
git remote -v
```

#### 3. Mantener Fork Actualizado

```bash
# Obtener cambios del repositorio original
git fetch upstream

# Mergear cambios a tu rama principal
git checkout master
git merge upstream/master

# Subir cambios a tu fork
git push origin master
```

## Configuración Post-Instalación

### Verificación de Dependencias Críticas

#### 1. Verificar Excel

```python
# Ejecutar en una consola Python
import xlwings as xw
try:
    app = xw.App(visible=False)
    app.quit()
    print("✓ Excel detectado correctamente")
except Exception as e:
    print(f"✗ Error con Excel: {e}")
```

#### 2. Verificar Dependencias Python

```bash
# Listar paquetes instalados
pip list

# Verificar paquetes críticos específicos
pip show xlwings pandas PyPDF2 pywin32
```

### Configuración de Desarrollo

#### Variables de Entorno (Opcional)

```bash
# Para desarrollo, agregar al PATH o .env
export PYTHONPATH="${PYTHONPATH}:./src"
```

#### Configuración de IDE

Para **VS Code**, crear `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

## Resolución de Problemas Comunes

### Error: "No module named 'xlwings'"

```bash
# Solución: Reinstalar xlwings
pip uninstall xlwings
pip install xlwings==0.28.5

# Verificar instalación
python -c "import xlwings; print(xlwings.__version__)"
```

### Error: "Excel application not found"

!!! danger "Problema Crítico"
    Este error indica que Excel no está instalado o no es accesible.

**Soluciones**:
1. Instalar Microsoft Excel (versión completa, no Excel Online)
2. Verificar que Excel se ejecuta correctamente
3. Ejecutar aplicación con permisos de administrador

### Error de Dependencias en Windows

```bash
# Instalar Visual C++ Redistributable
# Descargar desde: https://aka.ms/vs/17/release/vc_redist.x64.exe

# Actualizar pywin32 post-instalación
python -m pywin32_postinstall -install
```

### Problemas de Permisos

```bash
# Ejecutar con permisos elevados (Windows)
# Ejecutar terminal como administrador

# Verificar permisos de carpeta
icacls "C:\path\to\GestionExpedienteElectronico_Version1"
```

### Error: "ModuleNotFoundError: No module named 'tkinter'"

!!! info "Específico de Linux"
    En algunas distribuciones Linux, tkinter debe instalarse por separado.

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# CentOS/RHEL
sudo yum install tkinter
# o
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## Configuración Avanzada

### Build desde Código Fuente

Para crear un ejecutable personalizado:

```bash
# Instalar PyInstaller
pip install pyinstaller

# Crear ejecutable usando el spec file
pyinstaller config/main.spec

# El ejecutable estará en: dist/AgilEx_by_Marduk.exe
```

### Configuración de Logging

Crear archivo `logging.conf` en el directorio raíz:

```ini
[loggers]
keys=root

[handlers]
keys=fileHandler

[formatters]
keys=defaultFormatter

[logger_root]
level=INFO
handlers=fileHandler

[handler_fileHandler]
class=FileHandler
level=INFO
formatter=defaultFormatter
args=('logs/app.log',)

[formatter_defaultFormatter]
format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Variables de Configuración

Crear archivo `.env` (opcional):

```env
# Configuración de desarrollo
DEBUG=True
LOG_LEVEL=DEBUG
EXCEL_VISIBLE=False

# Configuración de rutas
TEMPLATE_PATH=src/assets/000IndiceElectronicoC0.xlsm
DATA_PATH=src/assets/
```

## Verificación Final

### Lista de Verificación

- [ ] Python 3.9.6+ instalado
- [ ] Microsoft Excel instalado y funcional
- [ ] Repositorio clonado correctamente
- [ ] Ambiente virtual creado y activado
- [ ] Dependencias instaladas sin errores
- [ ] Aplicación se ejecuta sin problemas
- [ ] Tests básicos pasan (opcional)

### Ejecutar Tests de Verificación

```bash
# Test básico de funcionalidad
python src/test/test.py

# Test de contador de páginas
python src/test/test_page_counter.py

# Test de manipulación Excel
python src/test/test_excel_manipulation.py
```

### Comando de Verificación Completa

```bash
# Script que verifica toda la instalación
python -c "
import sys
import xlwings as xw
import pandas as pd
from pathlib import Path

print(f'Python: {sys.version}')
print(f'xlwings: {xw.__version__}')
print(f'pandas: {pd.__version__}')

# Verificar Excel
try:
    app = xw.App(visible=False)
    app.quit()
    print('✓ Excel: OK')
except Exception as e:
    print(f'✗ Excel: {e}')

# Verificar archivos críticos
critical_files = [
    'src/__main__.py',
    'src/assets/000IndiceElectronicoC0.xlsm',
    'requirements.txt'
]

for file in critical_files:
    if Path(file).exists():
        print(f'✓ {file}: OK')
    else:
        print(f'✗ {file}: No encontrado')
"
```

---

!!! success "Instalación Completada"
    Si todos los checks pasan, tu instalación está lista. Continúa con la [Guía de Primeros Pasos](getting-started.md).