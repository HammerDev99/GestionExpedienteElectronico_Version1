# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Proyecto: GestionExpedienteElectronico_Version1

**Solución RDA (Robotic Desktop Automation)** para automatizar la creación de índices electrónicos de expedientes judiciales según los estándares del sistema judicial colombiano (PCSJA20-11567 de 2020).

**Versión Actual**: 1.4.4  
**Estado**: Refactorización activa en rama `refactor/processing-strategies`

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

## Arquitectura del Código (Estado Actual - Refactorizada y Unificada)

### Patrón MVC con Strategy Pattern Completamente Autónomo

La aplicación implementa una arquitectura modular y escalable con separación estricta de responsabilidades y flujo unificado.

#### **Model** (`src/model/`) - Lógica de Negocio Pura

- **`file_processor.py`**: Motor principal de procesamiento con integración Excel/xlwings
- **`metadata_extractor.py`**: Factory pattern para extracción de metadatos (PDF, Word, Excel)
- **`folder_analyzer.py`**: Análisis profundo de estructura de carpetas y validación CUI
- **`logger_config.py`**: Configuración centralizada de logging con rotación

#### **View** (`src/view/`) - Interfaz Gráfica Exclusivamente

- **`application.py`**: **COMPLETAMENTE UNIFICADA** - Responsabilidades estrictamente de GUI:
  - Creación y gestión de widgets Tkinter
  - Manejo de eventos de usuario (clicks, selecciones)
  - **Flujo 100% unificado**: `obtener_rutas()` y `procesa_expedientes()` idénticos para las 3 estrategias
  - **Eliminación total de duplicación**: Sin manejo diferenciado por `selected_value`
  - Gestión de estado visual de la aplicación
  - Control de versiones y actualizaciones
  - ~730 líneas de código limpio (reducción 20% por unificación)
- **`tooltip.py`**: Sistema de ayuda interactivo con imágenes
- **`tools_launcher.py`**: Ventana de herramientas adicionales

#### **Controller** (`src/controller/`) - Coordinación y Estrategias Completamente Autónomas

- **`processing_context.py`**: **SIMPLIFICADO** - Coordinador unificado del patrón Strategy
- **`process_strategy.py`**: **ESTRATEGIAS 100% AUTÓNOMAS**:
  - **`SingleCuadernoStrategy`**: Procesamiento independiente con `filedialog` propio
  - **`SingleExpedienteStrategy`**: Procesamiento autónomo de expediente (4 niveles)
  - **`MultiExpedienteStrategy`**: Procesamiento autónomo múltiple (5 niveles)
  - **Todas manejan**: Validación, selección de carpeta, confirmaciones, progreso y notificaciones
- **`gui_notifier.py`**: Patrón Observer unificado para todas las estrategias

### Responsabilidades de las Estrategias (100% Autónomas)

**CADA ESTRATEGIA ES COMPLETAMENTE INDEPENDIENTE** y maneja:

- **Selección de carpeta propia** con `filedialog.askdirectory()`
- **Validación de estructura** de carpetas específica según tipo
- **Validación de CUIs** (23 dígitos) con manejo dual string/set
- **Gestión de índices existentes** con confirmación de usuario
- **Análisis de directorios** y detección de problemas estructurales
- **Generación de mensajes** de advertencia específicos vía Observer
- **Confirmaciones de usuario** para procesamiento
- **Actualización de progreso** y notificaciones GUI
- **Manejo de errores** y recuperación autónoma
- **Procesamiento asíncrono** completo e independiente

### Tipos de Procesamiento Soportados (Flujo Unificado)

#### **1. Cuaderno Único** (`selected_value = "1"`) - **REFACTORIZADO**

- **Procesamiento 100% autónomo** por `SingleCuadernoStrategy`
- **Maneja su propia selección** de carpeta y confirmaciones
- **Validación CUI específica** con manejo de string individual
- **Detección automática** de anexos masivos
- Estructura plana con conteo directo de archivos

#### **2. Expediente Único** (`selected_value = "2"`) - **OPTIMIZADO**

- **Estructura jerárquica de 4 niveles** completamente autónoma
- **Validación completa** por `SingleExpedienteStrategy`
- **Manejo de CUIs en conjunto** con mensajes detallados
- Niveles: `Expediente → Instancia → Cuaderno → Archivos`

#### **3. Múltiples Expedientes** (`selected_value = "3"`) - **ESCALABLE**

- **Estructura jerárquica de 5 niveles** completamente autónoma
- **Procesamiento batch** por `MultiExpedienteStrategy`
- **Validación masiva de CUIs** con reportes consolidados
- Niveles: `Año → Expediente → Instancia → Cuaderno → Archivos`

### Patrones de Diseño Implementados (Refactorizados)

1. **Strategy Pattern**: **COMPLETAMENTE AUTÓNOMO** - Cada estrategia es independiente
2. **Observer Pattern**: **UNIFICADO** - Notificaciones GUI consistentes en tiempo real
3. **Factory Pattern**: Extractores de metadatos por tipo de archivo
4. **Dependency Injection**: Inyección de notificadores y loggers

### Flujo de Procesamiento Completamente Unificado

#### **Selección de Carpeta** (Totalmente Autónoma)

- **ELIMINADO**: `filedialog.askdirectory()` en `application.py`
- **IMPLEMENTADO**: Cada estrategia maneja su propia selección
- **RESULTADO**: Cero duplicación, máxima autonomía

#### **Confirmación de Procesamiento** (100% Consistente)

- **TODAS LAS ESTRATEGIAS**: Confirmación autónoma y consistente
- **ELIMINADO**: Manejo diferenciado por `selected_value`
- **RESULTADO**: Flujo idéntico para los 3 tipos de procesamiento

#### **Notificaciones GUI** (Patrón Observer Unificado)

- **Progreso**: Todas las estrategias usan `MessageType.PROGRESS`
- **Estado**: Todas usan `MessageType.STATUS` para barra de estado
- **Mensajes**: Todas usan `MessageType.TEXT` para log de actividad
- **Diálogos**: Todas usan `MessageType.DIALOG` para interacción usuario

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

### Funcionalidades Especializadas (Mejoradas)

- **Conteo automático de páginas** para PDF, Word, Excel
- **Manejo de documentos protegidos**/encriptados con recuperación
- **Extracción de metadatos** (fecha creación, tamaño, propiedades) vía Factory
- **Generación de índices Excel** con fórmulas automáticas
- **Procesamiento de subcarpetas** y detección automática de anexos
- **Validación dual de CUIs** (string individual / set múltiple) según estrategia
- **Validación completa de estructura** CUI (Código Único de Identificación) 23 dígitos
- **Mensajes de advertencia unificados** para problemas estructurales vía Observer
- **Detección inteligente de anexos masivos** con reportes detallados
- **Manejo de índices existentes** con confirmación y eliminación segura

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

### Consideraciones de Desarrollo (Arquitectura Modernizada)

- **Eliminación total de duplicación** entre GUI y estrategias
- **Código 20% más limpio** por unificación de flujos
- **Manejo robusto de errores** y validaciones 100% autónomas
- **Arquitectura altamente extensible** para nuevas estrategias
- **Flujo de usuario completamente unificado** sin diálogos duplicados
- **Patrón Observer consistente** para todas las interacciones GUI
- **Estrategias intercambiables** sin modificar `application.py`
- **Testabilidad mejorada** por aislamiento de responsabilidades
- **Actualizaciones automáticas** vía GitHub releases

### Archivos Críticos Actuales

- **Entry point**: `src/__main__.py`
- **GUI coordinadora**: `src/view/application.py` (refactorizada)
- **Estrategias autónomas**: `src/controller/process_strategy.py`
- **Coordinador**: `src/controller/processing_context.py`
- **Template Excel**: `src/assets/000IndiceElectronicoC0.xlsm`
- **Configuración build**: `config/main.spec`

### Principios de Desarrollo (Implementados y Mejorados)

- **Una sola responsabilidad**: Cada clase tiene un propósito específico y bien definido
- **DRY (Don't Repeat Yourself)**: **ELIMINACIÓN TOTAL** de duplicación de código
- **Bajo acoplamiento**: GUI y lógica de negocio **COMPLETAMENTE SEPARADAS**
- **Alta cohesión**: Funcionalidades relacionadas **100% AGRUPADAS** en estrategias autónomas
- **Principio Abierto/Cerrado**: Extensible para nuevas estrategias sin modificar código existente
- **Inversión de dependencias**: Estrategias dependen de abstracciones (Observer/Strategy)
- **Responsabilidad única**: `application.py` solo GUI, estrategias solo lógica específica
