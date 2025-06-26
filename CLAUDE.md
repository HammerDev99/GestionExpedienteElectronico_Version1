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

## Arquitectura del Código

### Patrón MVC Implementado
- **Model** (`src/model/`): Lógica de negocio y procesamiento de archivos
  - `file_processor.py`: Motor principal de procesamiento con integración Excel
  - `metadata_extractor.py`: Extracción de metadatos de documentos (PDF, Word, Excel)
  - `folder_analyzer.py`: Análisis de estructura de carpetas
  - `logger_config.py`: Configuración centralizada de logging

- **View** (`src/view/`): Interfaz gráfica con Tkinter
  - `application.py`: Ventana principal de la aplicación
  - `tooltip.py`: Sistema de ayuda interactivo con imágenes
  - `tools_launcher.py`: Ventana de herramientas adicionales

- **Controller** (`src/controller/`): Coordinación y flujo de procesamiento
  - `processing_context.py`: Coordinador del patrón Strategy
  - `process_strategy.py`: Estrategias de procesamiento (`SingleCuadernoStrategy`, `SingleExpedienteStrategy`, `MultiExpedienteStrategy`)
  - `gui_notifier.py`: Patrón Observer para notificaciones GUI

### Patrones de Diseño Clave

1. **Strategy Pattern**: Diferentes algoritmos de procesamiento según tipo de expediente
2. **Observer Pattern**: Notificaciones en tiempo real a la GUI
3. **Factory Pattern**: Creación de extractores de metadatos según tipo de archivo
4. **Singleton Pattern**: Configuración única de logging

### Gestión de Recursos
- `src/utils/resource_manager.py`: Manejo multiplataforma de rutas de recursos
- Detección automática de entorno (desarrollo vs producción empaquetada)
- Assets en `src/assets/`: templates Excel, datos de referencia, imágenes UI

### Dependencias Críticas
- **xlwings==0.28.5**: Automatización Excel (requiere Excel instalado)
- **pandas==1.5.2**: Manipulación de datos
- **PyPDF2==2.11.2**: Procesamiento de archivos PDF
- **pywin32==306**: Integración COM Windows
- **tkinter**: GUI (incluido en Python estándar)

### Tipos de Procesamiento Soportados
- **Cuaderno único**: Un solo documento en la carpeta
- **Expediente único**: Múltiples documentos en una carpeta
- **Múltiples expedientes**: Procesamiento batch de varias carpetas

### Funcionalidades Especializadas
- Conteo automático de páginas para PDF, Word, Excel
- Manejo de documentos protegidos/encriptados
- Extracción de metadatos (fecha creación, tamaño, propiedades)
- Generación de índices Excel con fórmulas automáticas
- Procesamiento de subcarpetas y anexos
- Validación de estructura CUI (Código Único de Identificación)

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
- El código maneja tanto ejecución directa Python como empaquetado PyInstaller
- Usa `getattr(sys, "frozen", False)` para detección de entorno
- Manejo robusto de errores y validaciones
- Interfaz multilenguaje preparada (español)
- Actualizaciones automáticas vía GitHub releases

### Archivos Críticos para Modificaciones
- Entry point: `src/__main__.py`
- Template Excel: `src/assets/000IndiceElectronicoC0.xlsm`
- Configuración build: `config/main.spec`
- Estrategias de procesamiento: `src/controller/process_strategy.py`