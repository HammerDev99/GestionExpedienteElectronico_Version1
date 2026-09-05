# Registro de cambios

Historial de versiones de **AgilEx by Marduk** (anteriormente GestionExpedienteElectronico).

El proyecto sigue [versionado semántico](https://semver.org/lang/es/). Para la distribución mediante instalador MSI, todo release debe incrementar alguno de los tres primeros campos de la versión: un cuarto campo (`1.5.2.1`) es invisible para el motor de actualización de Windows Installer.

> La documentación completa del proyecto está disponible en
> [docs.agilex.sprintjudicial.com](https://docs.agilex.sprintjudicial.com).

## Historial de versiones

- 2026-09-05 Nuevo Release 🚀 GestionExpedienteElectronico v1.5.2
  - Pipeline automatizado de empaquetado MSI y firma institucional: instalador WiX per-machine (con detección de aplicación en uso y actualización sin entradas duplicadas) y script de firma de 6 etapas para que el área de Seguridad Informática firme el ejecutable y el instalador con el certificado de la entidad, verificado de extremo a extremo.
  - Corrección previa de rutas de escritura que impedían el arranque de la aplicación instalada en Program Files.
  - Validación completa del instalador en equipo real: instalación silenciosa, metadatos en Agregar o quitar programas, accesos directos, desinstalación limpia, bloqueo de downgrade y actualización de versión sin generar entradas duplicadas.
  - Mitigación del congelamiento aparente de la interfaz durante el procesamiento de cargas grandes: la ventana deja de ser marcada como "No responde" por Windows mientras el proceso avanza.
  - El aviso de nueva versión disponible pasa a ser informativo: se mantiene la detección automática, pero se elimina la descarga directa del ejecutable para que la distribución se realice exclusivamente por el canal institucional, evitando instalaciones paralelas sin la firma de la entidad.
- 2026-04-20 Nuevo Release 🚀 GestionExpedienteElectronico v1.5.1
  - Re-firmado Authenticode del binario con certificado renovado tras el vencimiento del anterior (2026-03-04): algoritmo SHA256 + timestamp RFC 3161 (DigiCert TSA), cert vigente 2026-04-15 a 2029-04-15.
  - Actualización de metadatos PE (version_info.rc) a FileVersion/ProductVersion 1.5.1.0 y alineación del manifiesto UAC (app.manifest assemblyIdentity 1.5.1.0) para trazabilidad del build ante el SOC Rama Judicial.
  - Compilación definitiva en modo onefile (PyInstaller) para compatibilidad con entornos corporativos con ASR/AppLocker activos.
  - Sin cambios funcionales en el comportamiento de la aplicación respecto a 1.5.0; los cambios son exclusivamente de firma digital, metadatos y trazabilidad del binario.
- 2025-11-13 Nuevo Release 🚀 GestionExpedienteElectronico v1.5.0
  - Incorporación de enlaces directo en el menú de ayuda con acceso rápido a la documentación oficial de Agilex by Marduk facilitando el acceso a recursos de usuario básico y técnico, desde la interfaz de usuario.
  - Integración con Umami Analytics: Implementación de sistema de analytics básico y respetuoso con la privacidad para tracking de uso de la aplicación, enviando únicamente versión y eventos de inicio.
  - Validación ampliada de formatos de archivo: Soporte completo para archivos comprimidos (.zip, .rar, .7z), formatos de video adicionales (.avi, .mov, .mkv, .flv, .webm, .mpeg, .mpg, .m4v) y formatos de audio (.mp3, .wav, .wma, .aac, .flac, .ogg, .m4a), todos contabilizados como 1 página.
  - Mejoras de seguridad en metadatos del ejecutable: Actualización de version_info.rc con información institucional completa (Rama Judicial - CENDOJ), licencia MIT, descripción técnica detallada y validación "No malware" para optimizar resultados en análisis estático de seguridad (SAST) y reducir falsos positivos en VirusTotal.
  - Actualización de logo institucional: Implementación de logo oficial proporcionado por la UTDI de la Rama Judicial con configuración dual en ventana Tkinter y ejecutable empaquetado para visualización correcta.
  - Documentación técnica profesional con MkDocs: Implementación completa de documentación estructurada con MkDocs Material, incluyendo guías de usuario, API, arquitectura y deployment.
  - Refactorización del código de validación: Optimización de page_counter() usando conjuntos (set) para mejor legibilidad y mantenibilidad del código.
- 2025-07-08 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.5
  - Implementación de conversión de tamaños de archivo siguiendo estándares de OneDrive: Mejora significativa en la función size_units_converter para mostrar tamaños de archivo en unidades legibles con precisión y formato optimizado.
  - Refactorización completa del patrón Strategy: Implementación de arquitectura MVC con estrategias completamente autónomas que eliminan la duplicación de código y mejoran la modularidad del sistema.
  - Mejoras en la validación de CUIs: Optimización del manejo de radicados vacíos y mejora en los mensajes de notificación con detalles específicos sobre CUIs inválidos en todas las estrategias de procesamiento.
  - Optimización del sistema de logging: Mejoras en la calidad del registro de logs y reorganización estructural del proyecto con eliminación de archivos obsoletos.
- 2025-03-10 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.4
  - Refactorización de la interfaz de usuario para optimizar la gestión de carpetas: Mejoras significativas en la organización y procesamiento de expedientes en diversas condiciones, omitiendo automáticamente elementos no procesables.
  - Mejora en la comunicación con el usuario: Rediseño del formato de notificaciones para aumentar la legibilidad e incorporación de indicadores de progreso durante el procesamiento de carpetas seleccionadas.
  - Actualización de parámetros de indexación: Ajustes técnicos conforme a los requisitos establecidos por la Unidad de Transformación Digital durante la mesa funcional.
  - Gestión avanzada de subcarpetas: Implementación de manejo de anexos en el tipo de gestión "Expediente" y "Múltiples Expedientes" y mejora en la identificación de subcarpetas vacías.
  - Optimización del procesamiento de archivos: Eliminación de restricciones técnicas previas e implementación de filtros inteligentes para archivos del sistema.
  - Incorporación de banco de herramientas: Nueva ventana que proporciona recursos adicionales para los usuarios.
- 2025-02-15 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.3
  - Procesamiento avanzado de subcarpetas: La característica más destacada de esta versión, que permite gestionar estructuras jerárquicas de carpetas con validaciones automáticas y notificaciones claras.
  - Interfaz de usuario mejorada: Refinamientos en la GUI para proporcionar una experiencia más intuitiva, con mejor retroalimentación y nuevos controles.
  - Arquitectura y patrones de diseño renovados: Implementación de los patrones Observer y Estrategia para una gestión más modular y eficiente.
  - Rendimiento y optimizaciones: Mejoras técnicas para aumentar la velocidad y eficiencia del sistema.
  - Estabilidad y correcciones: Cambios orientados a mejorar la robustez y confiabilidad del software.
  - Eliminación de importaciones no utilizadas y optimización de estrategias de archivo.
- 2024-12-31 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.2
  - 2024-12-30 Implementación de gestión segura de índices existentes utilizando send2trash y mejoras en la validación del CUI
  - 2024-12-27 Optimización del procesamiento de carpetas con validación mejorada para estructuras vacías y manejo de errores
  - 2024-12-27 Refactorización completa del código para mejorar legibilidad y modularidad, especialmente en MetadataExtractor
  - 2024-12-27 Actualización del sistema de mensajes y validaciones para una mejor experiencia de usuario
  - 2024-12-19 Mejora significativa en la interfaz de usuario (GUI) con principios de progressive disclosure y nuevo menú de ayuda
- 2024-11-15 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.1
  - 2024-11-14 Actualización de documentación y mejoras en la funcionalidad general.
  - 2024-11-13 Mejoras significativas en la interfaz de usuario, corrección de errores menores y manejo de la estructura de carpetas con dos opciones de niveles.
- 2024-09-17 Nuevo Release 🚀 GestionExpedienteElectronico v1.3.0
  - 2024-09-17 Optimización en el manejo de archivos excel y mejora en el conteo del progressBar
  - 2024-09-17 eliminación de comentarios y agrega upperCase a primera letra
  - 2024-09-17 Agrega progressBar
  - 2024-09-17 Actualiza lista de modulos requeridos
  - 2024-09-17 Refactoriza el código para ajustar la configuración de carpetas para empaquetar
  - 2024-09-17 ajuste final con vulture
  - 2024-09-17 Agrega text widget con mensaje
  - 2024-09-17 actualiza funcionalidad de contar páginas en docx, doc y pdf protegido
  - 2024-09-17 Agregar datos adicionales a excel - Correccion de mensaje y ventana excel
  - 2024-09-13 Actualización del sistema funcional solo con pendientes mínimos
  - 2024-09-13 Actualización de procesamiento desde un nivel superior - PENDIENTES
  - 2024-09-13 Feature nueva para realizar proceso a varias carpetas
  - 2024-09-12 Refactorizar manejo de archivos del expediente electrónico
  - 2023-05-30 Set "DocumentoElectronico" into "nombres" list
  - 2023-05-29 Modifies index name format and enables cross-platform function. (v.1.0.1)
  - 2023-05-26 Identificando valores en variables de la función format_names
  - 2023-05-26 Versión estable
  - 2023-05-26 separa_cadena, renameFile2, type of encode line added, create_dataframe update
  - 2023-04-25 AutomatizacionEmpleado.py update
  - 2023-04-25 code path selector in cross platform form added for refactoring_base
  - 2023-01-24 update folder schema, add textchain class
  - 2022-12-16 add demo.gif
  - 2022-12-02 Update folder schema.
  - 2022-10-27 Add rda info
- 2022-10-26 First release 🚀. (v.1.0.0)
  - 2022-06-24 últimas actualizaciones
  - 2022-03-31 Actualiza lógica de los nombres
  - 2022-03-03 Create requirements.txt
  - 2022-03-02 Create LICENCE
  - 2022-02-18 Create README.md
  - 2022-02-02 GUI optimization
  - 2022-01-05 UpdateRepo
  - 2021-08-10 First use case with names format

