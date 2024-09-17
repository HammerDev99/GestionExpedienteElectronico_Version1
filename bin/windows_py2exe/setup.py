from distutils.core import setup
import py2exe

setup(
    name='GestionExpedienteElectronico',
    version='1.3',
    description='Descripción de tu aplicación',
    author='Daniel Arbelaez Alvarez',
    author_email='darbelaal@cendoj.ramajudicial.gov.co',
    windows=[{
        'script': 'app/main.py',  # El script principal de tu aplicación
        'icon_resources': [(1, 'law.ico')]  # Icono de la aplicación
    }],
    options={
        'py2exe': {
            'includes': [],  # Lista de módulos adicionales a incluir
            'excludes': [],  # Lista de módulos a excluir
            'dll_excludes': ['w9xpopen.exe'],  # DLLs a excluir
            'bundle_files': 1,  # Agrupar archivos en un solo ejecutable
            'compressed': True,  # Comprimir el ejecutable
        }
    },
    zipfile=None,  # No crear un archivo zip separado
    data_files=[('other_files', ['other_files/000IndiceElectronicoC0.xlsm'])]  # Archivos adicionales a incluir
)