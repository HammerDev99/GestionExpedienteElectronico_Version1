# Registro de Cambios

## Historial de Versiones

### 📦 Versión 1.5.2 - Septiembre 2026

**Distribución institucional mediante instalador MSI**

Esta versión introduce el empaquetado como instalador MSI firmado por el área de Seguridad Informática de la Rama Judicial, junto con las correcciones necesarias para que la aplicación opere instalada en `Program Files`.

#### Instalador MSI
- **Instalador WiX per-machine**: se instala para todos los usuarios del equipo y queda registrado en "Agregar o quitar programas", apto para despliegue por GPO o SCCM/Intune.
- **Actualización sin entradas duplicadas**: las versiones posteriores reemplazan la instalación anterior en lugar de acumularse.
- **Detección de aplicación en uso**: al actualizar o desinstalar con el programa abierto, el instalador solicita cerrarlo en lugar de exigir reiniciar el equipo.
- **Firma institucional**: el ejecutable y el instalador se firman con el certificado de la entidad mediante un procedimiento automatizado que ejecuta el área de Seguridad Informática.

#### Correcciones de compatibilidad
- **Rutas de escritura**: los registros de actividad se escriben en `%LOCALAPPDATA%`, no junto al ejecutable. Sin este cambio la aplicación no arrancaba instalada en `Program Files`, por ser un directorio de solo lectura.
- **Respuesta de la interfaz**: durante el procesamiento de cargas grandes la ventana deja de ser marcada como "No responde" por Windows.

#### Notificación de actualizaciones
- El aviso de nueva versión disponible pasa a ser **informativo**: se mantiene la detección automática, pero se elimina la descarga directa del ejecutable. La distribución se realiza exclusivamente por el canal institucional, evitando instalaciones paralelas sin la firma de la entidad.

#### Metadatos PE actualizados
- `FileVersion` y `ProductVersion` en `version_info.rc`: **1.5.2.0**.
- `assemblyIdentity version` en `app.manifest`: **1.5.2.0**.
- `last_version.json`: **1.5.2**.

> **Nota sobre versionado:** todo release distribuido debe incrementar alguno de los tres primeros campos de la versión. Un cuarto campo (`1.5.2.1`) es invisible para el motor de actualización de Windows Installer.

### 🔏 Versión 1.5.1 - Abril 2026

**Cambio de trazabilidad y re-firma digital (sin cambios funcionales)**

Esta versión no introduce modificaciones en el comportamiento del aplicativo. Los cambios son exclusivamente de firma digital, metadatos PE y trazabilidad del binario, en el marco de una gestión de mitigación de falsos positivos de detección con el área de Seguridad Informática de la Rama Judicial.

#### Firma digital renovada
- **Certificado de firma actualizado**: nuevo certificado SHA256 (RSA 4096) vigente del 2026-04-15 al 2029-04-15.
- **Algoritmo Authenticode**: SHA256 + Timestamp RFC 3161 (DigiCert TSA).
- **Modo de compilación definitivo**: PyInstaller onefile (compatibilidad con ASR/AppLocker en entornos corporativos).

#### Metadatos PE actualizados
- `FileVersion` y `ProductVersion` en `version_info.rc`: **1.5.1.0**.
- `assemblyIdentity version` en `app.manifest`: **1.5.1.0**.
- `last_version.json`: **1.5.1**.

#### Contexto
- Detección aislada de un motor antivirus, confirmada como falso positivo mediante validación externa (VirusTotal 1/72 motores, Microsoft Defender = Undetected).
- La distribución institucional (GPO/SCCM) se realiza mediante paquete `.msi` firmado por el área de Seguridad Informática con el certificado de la entidad — ver [Guía de Instalación](../user-guide/installation.md#opcion-3-distribucion-institucional-msi-firmado).

> El historial completo de versiones anteriores está disponible en el
> [CHANGELOG.md del repositorio](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/blob/master/CHANGELOG.md).

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

#### Versión 2.0.0
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