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

## Estructura de Testing

### Configuración de pytest

Crear `pytest.ini`:

```ini
[tool:pytest]
testpaths = src/test
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v 
    --tb=short 
    --strict-markers
    --disable-warnings
    --cov=src
    --cov-report=html:htmlcov
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    excel: Tests that require Excel
```

### Test Data y Fixtures

```bash
# Crear estructura de test data
mkdir -p src/test/test_data/{single_cuaderno,expediente,multi_expediente}
mkdir -p src/test/fixtures

# Archivos de prueba básicos
echo "Test content" > src/test/test_data/test_document.txt
```

### Ejemplo de Test Fixture

Crear `src/test/conftest.py`:

```python
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock

@pytest.fixture
def temp_folder():
    """Crear carpeta temporal para tests."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_excel_app():
    """Mock de aplicación Excel para tests sin Excel."""
    mock_app = MagicMock()
    mock_app.books = MagicMock()
    mock_app.quit = MagicMock()
    return mock_app

@pytest.fixture
def sample_cui():
    """CUI válido para tests."""
    return "12345678901234567890123"
```

## Scripts de Desarrollo Útiles

### Crear `scripts/dev_setup.py`

```python
#!/usr/bin/env python3
"""
Script de configuración automática del entorno de desarrollo.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Ejecutar comando con manejo de errores."""
    print(f"🔄 {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} completado")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}: {e}")
        return False
    return True

def main():
    """Configuración automática."""
    print("🚀 Configurando entorno de desarrollo...")
    
    # Verificar Python
    if not run_command("python --version", "Verificar Python"):
        return
    
    # Crear ambiente virtual si no existe
    if not Path(".venv").exists():
        run_command("python -m venv .venv", "Crear ambiente virtual")
    
    # Activar e instalar dependencias
    activate_cmd = ".venv\\Scripts\\Activate" if os.name == 'nt' else "source .venv/bin/activate"
    
    commands = [
        (f"{activate_cmd} && pip install --upgrade pip", "Actualizar pip"),
        (f"{activate_cmd} && pip install -r requirements.txt", "Instalar dependencias"),
        (f"{activate_cmd} && pre-commit install", "Configurar pre-commit"),
    ]
    
    for cmd, desc in commands:
        run_command(cmd, desc)
    
    print("🎉 Entorno de desarrollo configurado exitosamente!")

if __name__ == "__main__":
    main()
```

### Crear `scripts/run_tests.py`

```python
#!/usr/bin/env python3
"""
Script para ejecutar diferentes tipos de tests.
"""

import argparse
import subprocess
import sys

def run_tests(test_type="all", coverage=True, verbose=True):
    """Ejecutar tests con opciones configurables."""
    base_cmd = ["python", "-m", "pytest"]
    
    if verbose:
        base_cmd.append("-v")
    
    if coverage:
        base_cmd.extend(["--cov=src", "--cov-report=html"])
    
    if test_type == "unit":
        base_cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        base_cmd.extend(["-m", "integration"])
    elif test_type == "excel":
        base_cmd.extend(["-m", "excel"])
    elif test_type == "fast":
        base_cmd.extend(["-m", "not slow"])
    
    base_cmd.append("src/test/")
    
    print(f"🧪 Ejecutando tests: {test_type}")
    print(f"Comando: {' '.join(base_cmd)}")
    
    result = subprocess.run(base_cmd)
    return result.returncode == 0

def main():
    parser = argparse.ArgumentParser(description="Ejecutar tests del proyecto")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "excel", "fast"],
        default="all",
        help="Tipo de tests a ejecutar"
    )
    parser.add_argument("--no-coverage", action="store_true", help="Desactivar coverage")
    parser.add_argument("--quiet", action="store_true", help="Modo silencioso")
    
    args = parser.parse_args()
    
    success = run_tests(
        test_type=args.type,
        coverage=not args.no_coverage,
        verbose=not args.quiet
    )
    
    if success:
        print("✅ Todos los tests pasaron!")
        sys.exit(0)
    else:
        print("❌ Algunos tests fallaron")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Debugging Avanzado

### Configuración de Logging para Debug

Crear `src/debug_config.py`:

```python
import logging
import sys
from pathlib import Path

def setup_debug_logging():
    """Configurar logging para debugging detallado."""
    # Crear directorio de logs si no existe
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configurar logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(logs_dir / "debug.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Configurar loggers específicos
    loggers = [
        'src.model.file_processor',
        'src.controller.process_strategy',
        'src.view.application'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
    
    logging.info("Debug logging configurado")

if __name__ == "__main__":
    setup_debug_logging()
```

### Profiling de Performance

Crear `scripts/profile_app.py`:

```python
import cProfile
import pstats
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def profile_application():
    """Profile de la aplicación completa."""
    # Import después de agregar al path
    from src.__main__ import main
    
    # Ejecutar profiling
    pr = cProfile.Profile()
    pr.enable()
    
    # Aquí se ejecutaría la función a profilear
    # main()  # Descomentar para profilear main
    
    pr.disable()
    
    # Guardar resultados
    pr.dump_stats('profile_results.prof')
    
    # Mostrar top 20 funciones más lentas
    stats = pstats.Stats('profile_results.prof')
    stats.sort_stats('cumulative')
    stats.print_stats(20)

if __name__ == "__main__":
    profile_application()
```

## Flujo de Trabajo de Desarrollo

### Workflow Diario

1. **Activar ambiente virtual**
   ```bash
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # Linux/macOS
   ```

2. **Actualizar dependencias** (semanalmente)
   ```bash
   git pull upstream master
   pip install --upgrade -r requirements.txt
   ```

3. **Crear rama de feature**
   ```bash
   git checkout -b feature/nueva-funcionalidad
   ```

4. **Desarrollar con TDD**
   ```bash
   # Escribir test
   # Ejecutar test (debería fallar)
   python -m pytest src/test/test_nueva_funcionalidad.py -v
   
   # Implementar código
   # Ejecutar test (debería pasar)
   python -m pytest src/test/test_nueva_funcionalidad.py -v
   ```

5. **Verificar calidad de código**
   ```bash
   # Formatear código
   python -m black src/
   python -m isort src/
   
   # Verificar linting
   python -m flake8 src/
   
   # Ejecutar tests completos
   python -m pytest src/test/ --cov=src
   ```

6. **Commit y push**
   ```bash
   git add .
   git commit -m "feat: agregar nueva funcionalidad X"
   git push origin feature/nueva-funcionalidad
   ```

## Troubleshooting Común

### Problemas de Dependencias

```bash
# Limpiar cache de pip
pip cache purge

# Reinstalar dependencias desde cero
pip freeze > temp_requirements.txt
pip uninstall -r temp_requirements.txt -y
pip install -r requirements.txt
rm temp_requirements.txt
```

### Problemas de Import

```python
# Agregar al inicio de tests
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Problemas de Excel en Tests

```python
# Mock Excel para tests sin dependencia
import unittest.mock as mock

@mock.patch('xlwings.App')
def test_excel_function(mock_app):
    # Tu test aquí
    pass
```

---

!!! success "Entorno Listo"
    Con esta configuración tienes un entorno de desarrollo completo y profesional. Consulta el [CLAUDE.md](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/blob/master/CLAUDE.md) para conocer las mejores prácticas del proyecto.