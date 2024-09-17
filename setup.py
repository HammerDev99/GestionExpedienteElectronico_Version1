from setuptools import setup, find_packages

setup(
    name='GestionExpedienteElectronico',
    version='1.3.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'lxml==4.9.2',
        'numpy==1.23.5',
        'pandas==1.5.2',
        'psutil==5.9.5',
        'PyPDF2==2.11.2',
        'python-dateutil==2.8.2',
        'python-docx==1.1.2',
        'pytz==2023.3',
        'pywin32==306',
        'six==1.16.0',
        'tk==0.1.0',
        'typing_extensions==4.12.2',
        'xlwings==0.28.5',
    ],
    entry_points={
        'console_scripts': [
            'GestionExpedienteElectronico=your_project.main:main',
        ],
    },
)
