# -*- mode: python ; coding: utf-8 -*-
import sys
import os

# Datos adicionales de autoridad
author_name = "Daniel Arbelaez Alvarez"
author_email = "darbelaal@cendoj.ramajudicial.gov.co"
software_version = "1.5.0"

# Determinar sistema operativo
is_windows = sys.platform == 'win32'

# Obtener ruta base del proyecto de forma multiplataforma
BASEPATH = os.path.dirname(os.path.abspath('__file__'))

# Definir rutas de archivos de forma multiplataforma
def get_path(*paths):
    return os.path.join(BASEPATH, *paths)

# Configurar datos y binarios según plataforma
datas = [
    # Archivos de assets
    (get_path('src', 'assets', '000IndiceElectronicoC0.xlsm'), 'src/assets'),
    (get_path('src', 'assets', 'last_version.json'), 'src/assets'),
    (get_path('src', 'assets', 'law_logo.ico'), 'src/assets'),
    (get_path('src', 'assets', 'tooltip1.png'), 'src/assets'),
    (get_path('src', 'assets', 'tooltip2.png'), 'src/assets'),
    (get_path('src', 'assets', 'tooltip3.png'), 'src/assets'),
    (get_path('src', 'assets', 'TRD.csv'), 'src/assets'),
    (get_path('src', 'assets', 'JUZGADOS.csv'), 'src/assets'),
    (get_path('src', 'assets', 'last_version.json'), 'src/assets'),
    (get_path('src', 'assets', 'tools', 'Banco1.png'), 'src/assets/tools'),
    # Incluir explícitamente los módulos Python con su estructura
    (get_path('src', 'utils', 'resource_manager.py'), 'src/utils'),
    (get_path('src', 'model', 'metadata_extractor.py'), 'src/model'),
    (get_path('src', 'model', 'file_processor.py'), 'src/model'),
    (get_path('src', 'model', 'folder_analyzer.py'), 'src/model'),
    (get_path('src', 'model', 'logger_config.py'), 'src/model'),
    (get_path('src', 'view', 'application.py'), 'src/view'),
    (get_path('src', 'view', 'tools_launcher.py'), 'src/view'),
    (get_path('src', 'view', 'tooltip.py'), 'src/view'),
    (get_path('src', 'controller', 'process_strategy.py'), 'src/controller'),
    (get_path('src', 'controller', 'processing_context.py'), 'src/controller'),
    (get_path('src', 'controller', 'gui_notifier.py'), 'src/controller')
]

a = Analysis(
    [get_path('src', '__main__.py')],
    pathex=[BASEPATH],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter.ttk',
        'tkinter.filedialog',
        'send2trash',
        'certifi',
        'charset_normalizer',
        'idna',
        'numpy',
        'pandas',
        'PIL',
        'PIL.Image',           
        'PIL.ImageTk',        
        'PIL.ImageDraw',       
        'PIL.ImageFont',
        'psutil',
        'Crypto',
        'PyPDF2',   
        'dateutil', 
        'pytz',
        'win32com', 
        'win32api',
        'win32con',
        'win32com.client',
        'requests',
        'six',
        'urllib3',
        'xlwings'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    noarchive=False,
    optimize=0
)

pyz = PYZ(a.pure)

# Corregir rutas de archivos de configuración
version_info_path = get_path('src', 'assets', 'version_info.rc')
manifest_path = get_path('src', 'assets', 'app.manifest')

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'AgilEx_by_Marduk',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Desactivado para evitar falsos positivos en antivirus
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin ventana de consola para producción
    version=version_info_path,  # Metadatos de versión e información del producto
    manifest=manifest_path,  # Manifiesto UAC y compatibilidad Windows
    icon=get_path('src', 'assets', 'law_logo.ico'),  # Icono de la aplicación
    uac_admin=False,  # NO requiere permisos de administrador
    uac_uiaccess=False,  # NO requiere acceso UI Automation
    key=None,
    cert='docs\\others\\code_signing\\cert.pem'  # Certificado para firma (ignorado por PyInstaller, usar SignTool post-build)
)