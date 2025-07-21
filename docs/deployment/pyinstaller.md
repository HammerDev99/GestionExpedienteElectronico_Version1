# Build con PyInstaller

## Introducción

Esta guía cubre el proceso completo de empaquetado de GestionExpedienteElectronico_Version1 usando PyInstaller para crear ejecutables distribuibles en Windows.

## Configuración de PyInstaller

### Instalación de PyInstaller

```bash
# Activar ambiente virtual
.venv\Scripts\Activate  # Windows

# Instalar PyInstaller
pip install pyinstaller==5.13.0
```

!!! note "Versión Específica"
    Se recomienda usar PyInstaller 5.13.0 por compatibilidad verificada con xlwings y pywin32.

### Estructura de Archivos de Spec

El proyecto usa un archivo de configuración personalizado en `config/main.spec`:

```python
# -*- mode: python ; coding: utf-8 -*-
"""
Archivo de especificación PyInstaller para GestionExpedienteElectronico_Version1
Configuración optimizada para aplicación con GUI Tkinter y dependencias COM.
"""

import sys
from pathlib import Path

# Configuración de paths
project_root = Path().resolve()
src_path = project_root / 'src'
assets_path = src_path / 'assets'

# Configuración del análisis
block_cipher = None

a = Analysis(
    # Script principal
    [str(src_path / '__main__.py')],
    
    # Paths de búsqueda
    pathex=[
        str(project_root),
        str(src_path)
    ],
    
    # Binarios adicionales
    binaries=[],
    
    # Datos y recursos
    datas=[
        (str(assets_path), 'assets'),
        (str(assets_path / '000IndiceElectronicoC0.xlsm'), '.'),
        (str(assets_path / 'JUZGADOS.csv'), 'assets'),
        (str(assets_path / 'TRD.csv'), 'assets'),
        (str(assets_path / 'last_version.json'), 'assets'),
        (str(assets_path / '*.png'), 'assets'),
        (str(assets_path / '*.ico'), 'assets'),
        (str(assets_path / '*.icns'), 'assets'),
    ],
    
    # Módulos ocultos (imports dinámicos)
    hiddenimports=[
        'xlwings',
        'pandas',
        'PyPDF2',
        'pywin32',
        'win32com',
        'win32com.client',
        'pythoncom',
        'pywintypes',
        'PIL',
        'PIL.Image',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'tkinter.ttk',
        'send2trash',
        'pathlib',
        'logging.handlers',
        'csv',
        'json',
        'docx',
        'openpyxl'
    ],
    
    # Hooks adicionales
    hookspath=[],
    
    # Directorios runtime
    hooksconfig={},
    runtime_hooks=[],
    
    # Exclusiones
    excludes=[
        'matplotlib',
        'numpy.testing',
        'pytest',
        'unittest',
        'test'
    ],
    
    # Configuración adicional
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Configuración PYZ
pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

# Configuración del ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    
    # Configuración del ejecutable
    name='AgilEx_by_Marduk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    
    # Icono de la aplicación
    icon=str(assets_path / 'law_logo.ico'),
    
    # Información de versión (Windows)
    version=str(assets_path / 'version_info.rc'),
)

# Configuración COLLECT (para --onedir mode)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AgilEx_by_Marduk'
)
```

## Proceso de Build

### Build Manual

```bash
# Desde el directorio raíz del proyecto
pyinstaller config/main.spec

# El ejecutable se creará en:
# dist/AgilEx_by_Marduk.exe (modo --onefile)
# O en:
# dist/AgilEx_by_Marduk/ (modo --onedir)
```

### Build Automatizado con Script

Crear `scripts/build.py`:

```python
#!/usr/bin/env python3
"""
Script automatizado de build con PyInstaller.
Maneja limpieza, build, verificación y empaquetado.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path
import json
import datetime

class BuildManager:
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.dist_dir = self.project_root / 'dist'
        self.build_dir = self.project_root / 'build'
        self.spec_file = self.project_root / 'config' / 'main.spec'
        
    def clean_previous_builds(self):
        """Limpiar builds anteriores."""
        print("🧹 Limpiando builds anteriores...")
        
        for dir_path in [self.dist_dir, self.build_dir]:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Eliminado: {dir_path}")
        
        # Limpiar archivos .pyc
        for pyc_file in self.project_root.rglob('*.pyc'):
            pyc_file.unlink()
        
        # Limpiar directorios __pycache__
        for pycache_dir in self.project_root.rglob('__pycache__'):
            shutil.rmtree(pycache_dir)
    
    def verify_dependencies(self):
        """Verificar que todas las dependencias estén instaladas."""
        print("🔍 Verificando dependencias críticas...")
        
        critical_deps = [
            'xlwings',
            'pandas', 
            'PyPDF2',
            'pywin32',
            'Pillow',
            'send2trash'
        ]
        
        missing_deps = []
        for dep in critical_deps:
            try:
                __import__(dep)
                print(f"   ✅ {dep}")
            except ImportError:
                missing_deps.append(dep)
                print(f"   ❌ {dep}")
        
        if missing_deps:
            print(f"❌ Dependencias faltantes: {missing_deps}")
            return False
        
        return True
    
    def update_version_info(self):
        """Actualizar información de versión."""
        print("📝 Actualizando información de versión...")
        
        # Leer versión actual
        version_file = self.project_root / 'src' / 'assets' / 'last_version.json'
        if version_file.exists():
            with open(version_file, 'r') as f:
                version_data = json.load(f)
            version = version_data.get('version', '1.0.0')
        else:
            version = '1.0.0'
        
        # Crear archivo version_info.rc si no existe
        version_info_path = self.project_root / 'src' / 'assets' / 'version_info.rc'
        if not version_info_path.exists():
            self.create_version_info_file(version_info_path, version)
    
    def create_version_info_file(self, file_path: Path, version: str):
        """Crear archivo de información de versión para Windows."""
        version_parts = version.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')
        
        version_info_content = f"""
# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    prodvers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u'HammerDev99'),
           StringStruct(u'FileDescription', u'Gestión Expediente Electrónico'),
           StringStruct(u'FileVersion', u'{version}'),
           StringStruct(u'InternalName', u'AgilEx_by_Marduk'),
           StringStruct(u'LegalCopyright', u'© 2025 HammerDev99'),
           StringStruct(u'OriginalFilename', u'AgilEx_by_Marduk.exe'),
           StringStruct(u'ProductName', u'GestionExpedienteElectronico'),
           StringStruct(u'ProductVersion', u'{version}')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(version_info_content)
    
    def run_pyinstaller(self):
        """Ejecutar PyInstaller con el archivo spec."""
        print("🔨 Ejecutando PyInstaller...")
        
        cmd = ['pyinstaller', '--clean', str(self.spec_file)]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            print("   ✅ Build exitoso")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error en build: {e}")
            print(f"   STDOUT: {e.stdout}")
            print(f"   STDERR: {e.stderr}")
            return False
    
    def verify_build(self):
        """Verificar que el build se completó correctamente."""
        print("🧪 Verificando build...")
        
        exe_path = self.dist_dir / 'AgilEx_by_Marduk.exe'
        
        if not exe_path.exists():
            print(f"   ❌ Ejecutable no encontrado: {exe_path}")
            return False
        
        # Verificar tamaño del ejecutable
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"   📊 Tamaño del ejecutable: {size_mb:.2f} MB")
        
        if size_mb < 10:
            print("   ⚠️  Advertencia: Ejecutable muy pequeño, posibles dependencias faltantes")
        
        # Verificar que se puede ejecutar (test básico)
        try:
            # Test rápido: ejecutar con --help si existe esa opción
            # O simplemente verificar que no crashea inmediatamente
            result = subprocess.run(
                [str(exe_path)],
                timeout=10,
                capture_output=True
            )
            print("   ✅ Ejecutable puede iniciarse")
            return True
        except subprocess.TimeoutExpired:
            print("   ✅ Ejecutable iniciado correctamente (GUI)")
            return True
        except Exception as e:
            print(f"   ❌ Error al verificar ejecutable: {e}")
            return False
    
    def create_distribution_package(self):
        """Crear paquete de distribución."""
        print("📦 Creando paquete de distribución...")
        
        # Crear directorio de distribución
        dist_package_dir = self.project_root / f'distribution_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
        dist_package_dir.mkdir(exist_ok=True)
        
        # Copiar ejecutable
        exe_source = self.dist_dir / 'AgilEx_by_Marduk.exe'
        exe_dest = dist_package_dir / 'AgilEx_by_Marduk.exe'
        shutil.copy2(exe_source, exe_dest)
        
        # Crear README de distribución
        readme_content = f"""
# GestionExpedienteElectronico_Version1

## Instalación
1. Asegurar que Microsoft Excel esté instalado
2. Ejecutar AgilEx_by_Marduk.exe
3. Si Windows muestra advertencia de seguridad, seleccionar "Ejecutar de todos modos"

## Requisitos del Sistema
- Windows 10/11
- Microsoft Excel (requerido)
- 4GB RAM mínimo

## Fecha de Build
{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Soporte
- GitHub: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1
- Issues: https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/issues
"""
        
        with open(dist_package_dir / 'README.txt', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"   📦 Paquete creado en: {dist_package_dir}")
        return dist_package_dir
    
    def build(self):
        """Proceso completo de build."""
        print("🚀 Iniciando proceso de build...")
        
        steps = [
            ("Limpieza", self.clean_previous_builds),
            ("Verificación de dependencias", self.verify_dependencies),
            ("Actualización de versión", self.update_version_info),
            ("Build con PyInstaller", self.run_pyinstaller),
            ("Verificación de build", self.verify_build),
            ("Paquete de distribución", self.create_distribution_package)
        ]
        
        for step_name, step_func in steps:
            print(f"\n--- {step_name} ---")
            if not step_func():
                print(f"❌ Falló en: {step_name}")
                return False
        
        print("\n🎉 Build completado exitosamente!")
        return True

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build automatizado con PyInstaller")
    parser.add_argument("--clean-only", action="store_true", help="Solo limpiar builds anteriores")
    parser.add_argument("--verify-only", action="store_true", help="Solo verificar dependencias")
    
    args = parser.parse_args()
    
    builder = BuildManager()
    
    if args.clean_only:
        builder.clean_previous_builds()
    elif args.verify_only:
        builder.verify_dependencies()
    else:
        builder.build()

if __name__ == "__main__":
    main()
```

## Optimización del Build

### Reducir Tamaño del Ejecutable

#### 1. Exclusiones Específicas

```python
# En el archivo .spec, agregar más exclusiones
excludes=[
    # Módulos de testing
    'pytest', 'unittest', 'test', '_pytest',
    
    # Módulos científicos no usados
    'matplotlib', 'numpy.testing', 'scipy',
    
    # Módulos de desarrollo
    'IPython', 'jupyter', 'notebook',
    
    # Módulos de red no usados
    'requests', 'urllib3', 'chardet',
    
    # Otros módulos grandes no críticos
    'email', 'html', 'http', 'xml',
]
```

#### 2. Compresión UPX

```bash
# Instalar UPX (opcional)
# Descargar desde: https://upx.github.io/

# En el archivo .spec
upx=True,
upx_exclude=[
    'vcruntime140.dll',  # No comprimir DLLs críticas
    'python39.dll',
],
```

#### 3. Optimización de Assets

```python
# Solo incluir assets necesarios
datas=[
    (str(assets_path / '000IndiceElectronicoC0.xlsm'), '.'),
    (str(assets_path / 'JUZGADOS.csv'), 'assets'),
    (str(assets_path / 'TRD.csv'), 'assets'),
    (str(assets_path / 'last_version.json'), 'assets'),
    (str(assets_path / 'law_logo.ico'), 'assets'),
    # Excluir imágenes PNG grandes si no son críticas
]
```

### Performance del Ejecutable

#### 1. Modo de Empaquetado

```python
# Para distribución - un solo archivo (más lento de iniciar)
# En main.spec - usar configuración EXE actual

# Para desarrollo/testing - directorio (más rápido)
exe = EXE(
    pyz,
    a.scripts,
    [],  # No incluir binarios y datos aquí
    exclude_binaries=True,
    name='AgilEx_by_Marduk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AgilEx_by_Marduk'
)
```

#### 2. Lazy Loading de Módulos

```python
# En el código fuente, importar módulos pesados solo cuando se necesiten
def process_pdf_file(file_path):
    """Procesar archivo PDF con lazy import."""
    try:
        import PyPDF2  # Import solo cuando se necesita
        # ... lógica de procesamiento
    except ImportError:
        raise RuntimeError("PyPDF2 no disponible")
```

## Troubleshooting del Build

### Errores Comunes

#### 1. "Module not found" durante la ejecución

```python
# Solución: Agregar al hiddenimports en .spec
hiddenimports=[
    'modulo_faltante',
    'modulo_faltante.submodulo'
]
```

#### 2. Archivos de datos no encontrados

```python
# Verificar que las rutas en datas sean correctas
# Usar resource_manager para acceso multiplataforma
from src.utils.resource_manager import ResourceManager

# En lugar de:
template_path = "assets/template.xlsm"

# Usar:
template_path = ResourceManager.get_asset_path("template.xlsm")
```

#### 3. Problema con xlwings/Excel COM

```python
# Asegurar que estos imports estén en hiddenimports
hiddenimports=[
    'xlwings',
    'win32com',
    'win32com.client',
    'pythoncom',
    'pywintypes',
]

# También verificar que no haya conflictos de versión
pip show xlwings pywin32
```

#### 4. Error de DLLs faltantes

```bash
# Usar Dependency Walker o similar para identificar DLLs
# Luego agregar al spec file:

binaries=[
    ('C:\\Windows\\System32\\vcruntime140.dll', '.'),
    # Otras DLLs si es necesario
],
```

### Debugging del Build

#### 1. Build con Debug

```python
# Cambiar en .spec para debugging
exe = EXE(
    # ...
    debug=True,        # Habilitar debug
    console=True,      # Mostrar consola para ver errores
    # ...
)
```

#### 2. Verificar Imports

```python
# Crear script para verificar todos los imports
import pkgutil
import sys

def list_all_modules():
    """Listar todos los módulos disponibles."""
    for importer, modname, ispkg in pkgutil.iter_modules():
        print(f"Found module: {modname}")

if __name__ == "__main__":
    list_all_modules()
```

#### 3. Análisis de Tamaño

```bash
# Usar herramientas para analizar el tamaño del ejecutable
# PE Explorer (Windows) o similar
# O crear script de análisis:

python -c "
import os
from pathlib import Path

exe_path = Path('dist/AgilEx_by_Marduk.exe')
if exe_path.exists():
    size = exe_path.stat().st_size
    print(f'Executable size: {size / 1024 / 1024:.2f} MB')
else:
    print('Executable not found')
"
```

## Distribución del Ejecutable

### Checksum y Verificación

```python
# Crear checksums para verificación
import hashlib

def create_checksums(file_path):
    """Crear checksums MD5 y SHA256."""
    md5_hash = hashlib.md5()
    sha256_hash = hashlib.sha256()
    
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
            sha256_hash.update(chunk)
    
    return {
        "md5": md5_hash.hexdigest(),
        "sha256": sha256_hash.hexdigest()
    }
```

### Packaging Final

```bash
# Crear archivo ZIP para distribución
python -c "
import zipfile
from pathlib import Path

exe_path = Path('dist/AgilEx_by_Marduk.exe')
if exe_path.exists():
    with zipfile.ZipFile('AgilEx_by_Marduk_v1.4.5.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, 'AgilEx_by_Marduk.exe')
        zf.write('README.md', 'README.md')
        zf.write('LICENSE', 'LICENSE')
    print('Distribution package created: AgilEx_by_Marduk_v1.4.5.zip')
"
```

---

!!! success "Build Completado"
    Con esta configuración puedes crear ejecutables robustos y optimizados. Continúa con [Firma de Código](code-signing.md) para distribución segura.