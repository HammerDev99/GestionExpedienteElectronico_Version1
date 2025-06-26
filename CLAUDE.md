# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto: GestionExpedienteElectronico_Version1

**Solución RDA (Robotic Desktop Automation)** para automatizar la creación de índices electrónicos de expedientes judiciales según los estándares del sistema judicial colombiano (PCSJA20-11567 de 2020).

## Comandos Comunes de Desarrollo

### Configuración del Entorno
```bash
# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual (Windows)
.venv\Scripts\Activate

# Instalar dependencias
pip install --upgrade -r requirements.txt
```

### Ejecución
```bash
# Ejecutar aplicación en modo desarrollo
python src/__main__.py

# Ejecutar tests básicos
python src/test/test.py
python src/test/test_page_counter.py
python src/test/test_excel_manipulation.py
```

### Build y Empaquetado
```bash
# Crear ejecutable con PyInstaller
pyinstaller config/main.spec

# El ejecutable se genera en: dist/AgilEx_by_Marduk.exe
```

**Requisito crítico**: Microsoft Excel debe estar instalado para el funcionamiento correcto (usa xlwings para automatización COM).

## Arquitectura del Código (Estado Actual)

### Patrón MVC con Strategy Pattern Refinado
La aplicación implementa una arquitectura limpia con separación estricta de responsabilidades.

#### **Model** (`src/model/`) - Lógica de Negocio Pura
- **`file_processor.py`**: Motor principal de procesamiento con integración Excel/xlwings
- **`metadata_extractor.py`**: Factory pattern para extracción de metadatos (PDF, Word, Excel)
- **`folder_analyzer.py`**: Análisis profundo de estructura de carpetas y validación CUI
- **`logger_config.py`**: Configuración centralizada de logging con rotación

#### **View** (`src/view/`) - Interfaz Gráfica Exclusivamente
- **`application.py`**: Responsabilidades estrictamente de GUI:
  - Creación y gestión de widgets Tkinter
  - Manejo de eventos de usuario (clicks, selecciones)
  - Coordinación con estrategias (sin lógica de negocio)
  - Gestión de estado visual de la aplicación
  - Control de versiones y actualizaciones
  - ~870 líneas de código limpio
- **`tooltip.py`**: Sistema de ayuda interactivo con imágenes
- **`tools_launcher.py`**: Ventana de herramientas adicionales

#### **Controller** (`src/controller/`) - Coordinación y Estrategias Autónomas
- **`processing_context.py`**: Coordinador del patrón Strategy con inyección de dependencias
- **`process_strategy.py`**: Estrategias completas y autónomas:
  - **`SingleCuadernoStrategy`**: Procesamiento de documento único
  - **`SingleExpedienteStrategy`**: Procesamiento de expediente (4 niveles)
  - **`MultiExpedienteStrategy`**: Procesamiento múltiple (5 niveles)
- **`gui_notifier.py`**: Patrón Observer para notificaciones tiempo real

### Responsabilidades de las Estrategias (Autónomas)

Cada estrategia maneja completamente:
- **Validación de estructura** de carpetas específica
- **Validación de CUIs** (23 dígitos) con mensajes detallados
- **Gestión de índices existentes** con confirmación de usuario
- **Análisis de directorios** y detección de problemas estructurales
- **Generación de mensajes** de advertencia específicos
- **Confirmaciones de usuario** para procesamiento
- **Manejo de errores** y recuperación

### Tipos de Procesamiento Soportados

#### **1. Cuaderno Único** (`selected_value = "1"`)
- Procesamiento de documento único sin jerarquía
- Confirmación manejada por `application.py`
- Estructura plana, conteo directo de archivos

#### **2. Expediente Único** (`selected_value = "2"`)
- Estructura jerárquica de 4 niveles
- Validación completa autónoma por `SingleExpedienteStrategy`
- Niveles: `Expediente → Instancia → Cuaderno → Archivos`

#### **3. Múltiples Expedientes** (`selected_value = "3"`)
- Estructura jerárquica de 5 niveles
- Procesamiento batch por `MultiExpedienteStrategy`
- Niveles: `Año → Expediente → Instancia → Cuaderno → Archivos`

### Patrones de Diseño Implementados

1. **Strategy Pattern**: Estrategias completamente autónomas
2. **Observer Pattern**: Notificaciones GUI en tiempo real
3. **Factory Pattern**: Extractores de metadatos por tipo de archivo
4. **Dependency Injection**: Inyección de notificadores y loggers

### Flujo de Procesamiento Actual

#### **Selección de Carpeta** (Sin Duplicación)
- `application.py` realiza una única selección con `filedialog.askdirectory()`
- Pasa la carpeta seleccionada a las estrategias
- Las estrategias usan la carpeta recibida sin solicitar nueva selección

#### **Confirmación de Procesamiento** (Sin Duplicación)
- `selected_value = "1"`: Confirmación en `application.py`
- `selected_value = "2"` y `"3"`: Confirmación autónoma en cada estrategia
- Una sola confirmación por tipo de procesamiento

### Gestión de Recursos
- **`src/utils/resource_manager.py`**: Manejo multiplataforma de rutas
- **Detección automática**: Entorno desarrollo vs producción empaquetada
- **Assets**: `src/assets/` contiene templates Excel, datos de referencia, imágenes UI

### Dependencias Críticas
- **xlwings==0.28.5**: Automatización Excel (requiere Excel instalado)
- **pandas==1.5.2**: Manipulación de datos
- **PyPDF2==2.11.2**: Procesamiento de archivos PDF
- **pywin32==306**: Integración COM Windows
- **tkinter**: GUI (incluido en Python estándar)

### Funcionalidades Especializadas
- Conteo automático de páginas para PDF, Word, Excel
- Manejo de documentos protegidos/encriptados
- Extracción de metadatos (fecha creación, tamaño, propiedades)
- Generación de índices Excel con fórmulas automáticas
- Procesamiento de subcarpetas y anexos
- Validación completa de estructura CUI (Código Único de Identificación)
- Mensajes de advertencia detallados para problemas estructurales

### Datos de Configuración
- `src/assets/JUZGADOS.csv`: Datos de referencia de juzgados
- `src/assets/TRD.csv`: Clasificación de tipos documentales
- `src/assets/000IndiceElectronicoC0.xlsm`: Template Excel para índices
- `src/assets/last_version.json`: Control de versiones

### Logging y Monitoreo
- Logs automáticos en directorio `logs/`
- Niveles: DEBUG, INFO, WARNING, ERROR
- Seguimiento de excepciones y rendimiento
- Monitoreo de procesos Excel para evitar zombies

### Consideraciones de Desarrollo
- Código limpio sin duplicación entre GUI y estrategias
- Manejo robusto de errores y validaciones autónomas
- Arquitectura extensible para nuevas estrategias
- Flujo de usuario fluido sin diálogos duplicados
- Actualizaciones automáticas vía GitHub releases

### Archivos Críticos Actuales
- **Entry point**: `src/__main__.py`
- **GUI coordinadora**: `src/view/application.py` (refactorizada)
- **Estrategias autónomas**: `src/controller/process_strategy.py`
- **Coordinador**: `src/controller/processing_context.py`
- **Template Excel**: `src/assets/000IndiceElectronicoC0.xlsm`
- **Configuración build**: `config/main.spec`

### Principios de Desarrollo
- **Una sola responsabilidad**: Cada clase tiene un propósito específico
- **Sin duplicación**: Una sola fuente de verdad por funcionalidad
- **Bajo acoplamiento**: GUI y lógica de negocio separadas
- **Alta cohesión**: Funcionalidades relacionadas agrupadas en estrategias