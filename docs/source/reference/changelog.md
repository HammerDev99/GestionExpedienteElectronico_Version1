# Registro de Cambios

## Historial de Versiones

### 🔏 Versión 1.5.1 - Abril 2026

**Cambio de trazabilidad y re-firma digital (sin cambios funcionales)**

Esta versión no introduce modificaciones en el comportamiento del aplicativo. Los cambios son exclusivamente de firma digital, metadatos PE y trazabilidad del binario, en el marco de la gestión del incidente XDR 804977 con el SOC de la Rama Judicial.

#### Firma digital renovada
- **Certificado de firma actualizado**: nuevo certificado self-signed SHA256 (RSA 4096) vigente del 2026-04-15 al 2029-04-15.
- **Thumbprint estable**: `92ADA07AA3455816E2555C6CDF8D5120AE7D57B1` (utilizable como criterio de whitelist).
- **Algoritmo Authenticode**: SHA256 + Timestamp RFC 3161 (DigiCert TSA).
- **Modo de compilación definitivo**: PyInstaller onefile (compatibilidad con ASR/AppLocker en entornos corporativos).

#### Metadatos PE actualizados
- `FileVersion` y `ProductVersion` en `version_info.rc`: **1.5.1.0**.
- `assemblyIdentity version` en `app.manifest`: **1.5.1.0**.
- `last_version.json`: **1.5.1**.

#### Contexto
- Incidente SOC Rama Judicial: `804977` / `RJ-MDE-MAL-ALERT-002` (detección "Malgent" — falso positivo).
- Validación externa: VirusTotal 1/72 motores, Microsoft Defender = Undetected.
- Trámite paralelo: certificado comercial EV Code Signing con Andes SCD (white-label Sectigo, raíz incluida en Microsoft Trusted Root Program), validado técnicamente el 2026-04-20.

### 🚀 Versión 1.5.0 - Noviembre 2025

**Release funcional previa — integración con Umami Analytics y validación ampliada de formatos**

- Incorporación de enlaces directos a la documentación oficial en el menú de ayuda.
- Integración con Umami Analytics (privacy-respecting, solo versión y evento de inicio).
- Validación ampliada de formatos: archivos comprimidos (.zip, .rar, .7z), video (.avi, .mov, .mkv, .flv, .webm, .mpeg, .mpg, .m4v) y audio (.mp3, .wav, .wma, .aac, .flac, .ogg, .m4a).
- Actualización de metadatos PE del ejecutable con información institucional completa.
- Actualización de logo institucional (UTDI Rama Judicial).
- Documentación técnica profesional con MkDocs Material.
- Refactorización de validaciones usando conjuntos (`set`).

### 🚀 Versión 1.4.5 - Julio 2025

**Mejoras Principales:**

#### Conversión de Tamaños de Archivo
- **Nueva implementación** de `size_units_converter` en MetadataExtractor
- **Estándares OneDrive**: Conversión precisa siguiendo reglas de OneDrive
- **Unidades legibles**: Automática conversión a KB, MB, GB con precisión optimizada
- **Formato mejorado**: Presentación consistente de tamaños de archivo

#### Refactorización Completa del Patrón Strategy
- **Arquitectura MVC completamente autónoma**: Estrategias 100% independientes
- **Eliminación total de duplicación**: Reducción del 20% en líneas de código
- **Flujo unificado**: `obtener_rutas()` y `procesa_expedientes()` idénticos para las 3 estrategias
- **Strategies autosuficientes**: Cada estrategia maneja su propia selección, validación y confirmaciones

#### Mejoras en Validación de CUIs
- **Optimización del manejo de radicados vacíos**: Mejor detección y procesamiento
- **Mensajes específicos**: Notificaciones detalladas sobre CUIs inválidos
- **Validación dual**: Soporte para CUI individual (string) y múltiple (set)
- **Reportes consolidados**: Información clara sobre problemas de validación

#### Sistema de Logging Optimizado
- **Calidad mejorada**: Mejor registro de eventos y errores
- **Reorganización estructural**: Eliminación de archivos obsoletos
- **Rotación eficiente**: Gestión automática de logs históricos
- **Monitoreo detallado**: Seguimiento granular de operaciones

### 🚀 Versión 1.4.4 - Marzo 2025

**Refactorización de Interfaz:**

#### Gestión Optimizada de Carpetas
- **Procesamiento mejorado**: Mejor manejo de expedientes en diversas condiciones
- **Omisión automática**: Exclusión inteligente de elementos no procesables
- **Gestión avanzada de subcarpetas**: Manejo especializado de anexos
- **Filtros inteligentes**: Exclusión automática de archivos del sistema

#### Comunicación con Usuario
- **Formato rediseñado**: Notificaciones más legibles y claras
- **Indicadores de progreso**: Seguimiento visual durante procesamiento
- **Identificación de subcarpetas vacías**: Detección y reporte automático
- **Mensajes contextuales**: Información específica según el tipo de procesamiento

#### Actualizaciones Técnicas
- **Parámetros de indexación**: Ajustes según requisitos de Transformación Digital
- **Eliminación de restricciones**: Mayor flexibilidad en tipos de archivo
- **Banco de herramientas**: Nueva ventana con recursos adicionales

### 🚀 Versión 1.4.3 - Febrero 2025

**Procesamiento Avanzado de Subcarpetas:**

#### Nueva Funcionalidad Destacada
- **Gestión jerárquica**: Procesamiento de estructuras de carpetas complejas
- **Validaciones automáticas**: Verificación de compliance con estándares
- **Notificaciones claras**: Reportes detallados de estructura y problemas

#### Interfaz de Usuario Refinada
- **GUI mejorada**: Experiencia más intuitiva y responsive
- **Retroalimentación mejorada**: Mejor comunicación de estado y progreso
- **Nuevos controles**: Elementos de interfaz adicionales para mejor control

#### Arquitectura Renovada
- **Patrón Observer**: Implementación para notificaciones en tiempo real
- **Patrón Strategy**: Gestión modular de diferentes tipos de procesamiento
- **Modularidad mejorada**: Arquitectura más mantenible y extensible

#### Rendimiento y Estabilidad
- **Optimizaciones técnicas**: Mejor velocidad de procesamiento
- **Robustez mejorada**: Manejo de errores más resiliente
- **Eliminación de imports no utilizados**: Código más limpio

### 🚀 Versión 1.4.2 - Diciembre 2024

**Gestión Segura y Validación Mejorada:**

#### Manejo de Índices Existentes
- **send2trash integration**: Eliminación segura de índices previos
- **Confirmación de usuario**: Diálogos de confirmación antes de reemplazar
- **Recuperación posible**: Archivos enviados a papelera de reciclaje

#### Validación de CUI Mejorada
- **Detección robusta**: Mejor identificación de CUIs de 23 dígitos
- **Mensajes específicos**: Retroalimentación clara sobre problemas de validación
- **Manejo de casos edge**: Procesamiento de situaciones límite

#### Optimización de Carpetas
- **Validación de estructuras vacías**: Detección de carpetas sin contenido válido
- **Manejo de errores mejorado**: Recuperación automática de errores comunes
- **Mensajes de usuario**: Comunicación clara de problemas y soluciones

#### Refactorización de Código
- **MetadataExtractor mejorado**: Código más legible y modular
- **Mejor organización**: Estructura de código más mantenible
- **Principios de progressive disclosure**: Interfaz menos abrumadora

### 🚀 Versión 1.4.1 - Noviembre 2024

**Mejoras de Interfaz y Funcionalidad:**

#### Interfaz de Usuario
- **Correcciones de GUI**: Elementos visuales refinados
- **Manejo de errores**: Mejor comunicación de problemas al usuario
- **Estructura de carpetas**: Soporte para opciones de niveles múltiples

#### Documentación y Mantenimiento
- **Actualización de docs**: Documentación técnica mejorada
- **Correcciones menores**: Bugs identificados y resueltos
- **Estabilidad general**: Mejoras en robustez del sistema

### 🚀 Versión 1.3.0 - Septiembre 2024

**Optimizaciones y Nuevas Características:**

#### Manejo de Excel Mejorado
- **Optimización de archivos Excel**: Mejor rendimiento con hojas de cálculo
- **Progreso visual**: Implementación de barra de progreso
- **Uppercase automático**: Primera letra en mayúscula automáticamente

#### Funcionalidades Adicionales
- **Widget de texto**: Mensajes informativos mejorados
- **Conteo de páginas mejorado**: Soporte para DOCX, DOC y PDFs protegidos
- **Datos adicionales en Excel**: Más metadatos incluidos automáticamente

#### Refactorización y Limpieza
- **Configuración de carpetas**: Ajustes para empaquetado optimizado
- **Código limpio**: Eliminación de código obsoleto con vulture
- **Modularidad**: Mejor organización del código fuente

### 🚀 Versión 1.0.1 - Mayo 2023

**Correcciones y Mejoras:**

#### Multiplataforma
- **Compatibilidad mejorada**: Función multiplataforma habilitada
- **Formato de nombres**: Modificación del formato de índices
- **Codificación**: Manejo mejorado de caracteres especiales

#### Funcionalidades
- **Separación de cadenas**: Mejor procesamiento de nombres de archivo
- **Renombrado de archivos**: Funcionalidad mejorada
- **DataFrames**: Creación optimizada de estructuras de datos

### 🚀 Versión 1.0.0 - Octubre 2022

**Primer Lanzamiento Oficial:**

#### Funcionalidades Principales
- **GUI básica**: Interfaz gráfica funcional con Tkinter
- **Procesamiento de archivos**: Soporte para PDF, Word, Excel
- **Generación de índices**: Creación automática de índices Excel
- **Metadatos básicos**: Extracción de información fundamental

#### Casos de Uso
- **Formato de nombres**: Lógica de nomenclatura implementada
- **Optimización GUI**: Interfaz refinada y funcional
- **Integración Excel**: Automatización básica con COM

## Histórico de Desarrollo

### Fases de Desarrollo

#### Fase 1: Conceptualización (2021-2022)
- **Identificación de necesidad**: Automatización de índices judiciales
- **Prototipo inicial**: Primer caso de uso con formato de nombres
- **GUI básica**: Implementación de interfaz rudimentaria

#### Fase 2: Funcionalidad Core (2022-2023)
- **Motor de procesamiento**: Lógica central implementada
- **Integración Excel**: Automatización COM funcional
- **Manejo de archivos**: Soporte básico para formatos principales

#### Fase 3: Refinamiento (2023-2024)
- **Interfaz mejorada**: GUI más intuitiva y funcional
- **Robustez**: Manejo de errores y casos edge
- **Performance**: Optimizaciones de velocidad y memoria

#### Fase 4: Arquitectura Avanzada (2024-2025)
- **Patrones de diseño**: Strategy, Observer, Factory implementados
- **Modularidad**: Separación estricta de responsabilidades
- **Escalabilidad**: Arquitectura preparada para crecimiento

## Roadmap Futuro

### Próximas Versiones Planeadas

#### Versión 1.5.0 (Estimada: Q3 2025)
- **Soporte multiplataforma completo**: Linux y macOS
- **API REST**: Interfaz para integración con otros sistemas
- **Procesamiento en lote**: Automatización de grandes volúmenes
- **Templates personalizables**: Configuración de formatos de salida

#### Versión 2.0.0 (Estimada: Q4 2025)
- **Interfaz web**: GUI moderna basada en navegador
- **Base de datos integrada**: Persistencia de configuraciones
- **Autenticación**: Control de acceso y usuarios
- **Reportes avanzados**: Dashboards y analytics

### Funcionalidades en Consideración

#### Integraciones
- **Servicios en la nube**: Google Drive, OneDrive, SharePoint
- **Sistemas judiciales**: Integración directa con plataformas oficiales
- **OCR avanzado**: Reconocimiento de texto en imágenes

#### Mejoras de Usuario
- **Asistente de configuración**: Setup guiado para nuevos usuarios
- **Plantillas predefinidas**: Configuraciones por tipo de juzgado
- **Validación en tiempo real**: Feedback inmediato durante configuración

## Contribuciones y Créditos

### Desarrollador Principal
**HammerDev99** - Arquitectura, implementación y mantenimiento principal

### Agradecimientos Especiales
- **Comunidad judicial colombiana**: Feedback y requisitos funcionales
- **Unidad de Transformación Digital**: Estándares técnicos y validación
- **Beta testers**: Identificación de bugs y casos de uso reales

### Licencias y Dependencias
- **MIT License**: Licencia principal del proyecto
- **Python ecosystem**: pandas, xlwings, PyPDF2, pywin32
- **Microsoft Excel**: Integración COM para automatización

---

!!! info "Mantente Actualizado"
    Para recibir notificaciones de nuevas versiones, síguenos en [@hammerdev99](https://twitter.com/hammerdev99) o watch el [repositorio en GitHub](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1).