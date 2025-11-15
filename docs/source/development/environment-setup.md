# Configuración del Entorno de Desarrollo

## Introducción

Esta guía te ayudará a configurar un entorno de desarrollo completo para GestionExpedienteElectronico_Version1, incluyendo herramientas de desarrollo, debugging, testing y contribución al proyecto.

## Prerrequisitos de Desarrollo

### Software Obligatorio

#### Python 3.9.6+
```bash
# Verificar versión instalada
python --version

# Si necesitas instalar Python, descargar desde:
# https://www.python.org/downloads/
```

#### Git
```bash
# Verificar instalación
git --version

# Configurar Git (si es primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu.email@example.com"
```

#### Microsoft Excel
!!! warning "Crítico para Desarrollo"
    Excel debe estar instalado para testing y debugging de la funcionalidad core de automatización COM.

### IDEs y Editores Recomendados

#### Visual Studio Code (Recomendado)

**Extensiones esenciales:**
```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "ms-python.flake8",
        "ms-python.isort",
        "ms-toolsai.jupyter",
        "redhat.vscode-yaml",
        "yzhang.markdown-all-in-one"
    ]
}
```

#### PyCharm Professional (Alternativa)
- Configuración automática de ambientes virtuales
- Debugging avanzado
- Integración Git integrada
- Refactoring tools

## Configuración del Proyecto

### 1. Clonar y Configurar Repositorio

```bash
# Opción A: Clonar repositorio principal
git clone https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git
cd GestionExpedienteElectronico_Version1

# Opción B: Fork + Clone (para contribuciones)
# 1. Hacer fork en GitHub web interface
# 2. Clonar tu fork
git clone https://github.com/TU-USUARIO/GestionExpedienteElectronico_Version1.git
cd GestionExpedienteElectronico_Version1

# 3. Agregar upstream
git remote add upstream https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git
```

### 2. Ambiente Virtual y Dependencias

#### Crear y Activar Ambiente Virtual
```bash
# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual
# Windows:
.venv\Scripts\Activate
# Linux/macOS:
source .venv/bin/activate

# Verificar activación (debería mostrar (.venv) en el prompt)
which python  # Linux/macOS
where python   # Windows
```

#### Instalar Dependencias de Desarrollo
```bash
# Dependencias básicas
pip install --upgrade pip
pip install -r requirements.txt

# Dependencias adicionales para desarrollo
pip install --upgrade \
    pytest>=6.0.0 \
    pytest-cov>=2.0.0 \
    black>=22.0.0 \
    flake8>=4.0.0 \
    isort>=5.0.0 \
    mypy>=0.991 \
    pre-commit>=2.0.0 \
    mkdocs-material>=8.0.0 \
    mkdocstrings[python]>=0.19.0
```

### 3. Configuración de Pre-commit Hooks

```bash
# Instalar pre-commit
pip install pre-commit

# Configurar hooks (crear .pre-commit-config.yaml)
cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black
        args: [--line-length=88]
  
  - repo: https://github.com/pycqa/isort
    rev: 5.11.4
    hooks:
      - id: isort
        args: [--profile=black]
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88, --extend-ignore=E203]
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.991
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
EOF

# Instalar hooks
pre-commit install
```

## Configuración del IDE

### Visual Studio Code

#### 1. Configuración de Workspace
Crear `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/Scripts/python.exe",
    "python.envFile": "${workspaceFolder}/.env",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.flake8Args": [
        "--max-line-length=88",
        "--extend-ignore=E203"
    ],
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--line-length=88"
    ],
    "python.sortImports.path": "isort",
    "python.sortImports.args": [
        "--profile=black"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "src/test"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "build/": true,
        "dist/": true,
        ".pytest_cache/": true
    }
}
```

#### 2. Launch Configuration
Crear `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Main Application",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/src/__main__.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}",
            "env": {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        },
        {
            "name": "Debug Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": [
                "src/test/",
                "-v",
                "--tb=short"
            ],
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        },
        {
            "name": "Debug Specific Strategy",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/debug_strategy.py",
            "console": "integratedTerminal",
            "args": [
                "SingleCuadernoStrategy"
            ]
        }
    ]
}
```

#### 3. Tasks Automation
Crear `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Format Code",
            "type": "shell",
            "command": "${config:python.defaultInterpreterPath}",
            "args": ["-m", "black", "src/"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "silent",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Sort Imports",
            "type": "shell",
            "command": "${config:python.defaultInterpreterPath}",
            "args": ["-m", "isort", "src/"],
            "group": "build"
        },
        {
            "label": "Lint Code",
            "type": "shell",
            "command": "${config:python.defaultInterpreterPath}",
            "args": ["-m", "flake8", "src/"],
            "group": "test"
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "${config:python.defaultInterpreterPath}",
            "args": ["-m", "pytest", "src/test/", "-v"],
            "group": "test"
        },
        {
            "label": "Build Executable",
            "type": "shell",
            "command": "${config:python.defaultInterpreterPath}",
            "args": ["-m", "PyInstaller", "config/main.spec"],
            "group": "build"
        }
    ]
}
```

## Variables de Entorno de Desarrollo

### Crear archivo `.env`

```env
# Configuración de desarrollo
DEBUG=True
LOG_LEVEL=DEBUG
EXCEL_VISIBLE=False

# Rutas de recursos (desarrollo)
TEMPLATE_PATH=src/assets/000IndiceElectronicoC0.xlsm
DATA_PATH=src/assets/
LOGS_PATH=logs/

# Configuración de testing
PYTEST_TIMEOUT=30
TEST_DATA_PATH=src/test/test_data/

# Configuración de build
BUILD_MODE=development
VERSION_CHECK=True
```

### Cargar Variables en Python

```python
# En archivos que necesiten configuración
import os
from pathlib import Path

# Cargar variables de entorno
if Path('.env').exists():
    from dotenv import load_dotenv
    load_dotenv()

DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
```

---

!!! success "Entorno Listo"
    Con esta configuración tienes un entorno de desarrollo completo y profesional. Consulta el [CLAUDE.md](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/blob/master/CLAUDE.md) para conocer las mejores prácticas del proyecto.