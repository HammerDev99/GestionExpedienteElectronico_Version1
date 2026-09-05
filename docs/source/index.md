# AgilEx

<div align="center">
  <img src="assets/UTDI_Mesa-de-trabajo-1Logo_Agilex.webp" alt="Logo AgilEx" width="300"/>
</div>

## Bienvenido a la Documentación

**AgilEx** (anteriormente conocido como GestionExpedienteElectronico) es una solución RDA (Robotic Desktop Automation) diseñada para automatizar la creación de índices electrónicos de expedientes judiciales siguiendo los estándares del sistema judicial colombiano establecidos en el protocolo PCSJA20-11567 de 2020.

![Demo de la aplicación](assets/Demo.gif)

## ¿Qué es AgilEx?

Esta aplicación permite realizar de forma automatizada la **creación y diligenciamiento** del formato índice electrónico con los metadatos de los archivos alojados en una carpeta específica. Los archivos (documentos) conforman un expediente electrónico y mediante este software se crea **desde cero** el índice del mismo.

### Características Principales

- **🚀 Automatización Completa**: Procesamiento automatizado de expedientes judiciales
- **📊 Extracción de Metadatos**: Obtención automática de información de documentos PDF, Word y Excel
- **🏗️ Arquitectura Modular**: Implementación de patrones MVC y Strategy para máxima extensibilidad
- **📝 Múltiples Tipos de Procesamiento**: Soporte para cuadernos únicos, expedientes individuales y múltiples expedientes
- **🔍 Validación Inteligente**: Verificación automática de estructura de carpetas y CUIs (Código Único de Identificación)
- **📋 Generación de Índices Excel**: Creación automática de índices con fórmulas y formato estándar

### Versión Actual

**Versión 1.5.1** - Abril 2026

Release de trazabilidad y firma digital (sin cambios funcionales respecto
a 1.5.0). Ver el [registro de cambios completo](reference/changelog.md)
para el historial de versiones.

## Inicio Rápido

### Prerrequisitos

- Python 3.9.6 o superior
- Microsoft Excel (requerido para automatización COM)
- Windows (recomendado para funcionalidad completa)

### Instalación Básica

```bash
# Clonar el repositorio
git clone https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git

# Navegar al directorio
cd GestionExpedienteElectronico_Version1

# Crear ambiente virtual
python -m venv .venv

# Activar ambiente virtual (Windows)
.venv\Scripts\Activate

# Instalar dependencias
pip install --upgrade -r requirements.txt

# Ejecutar la aplicación
python src/__main__.py
```

## Navegación de la Documentación

### Para Usuarios

- **[Guía del Usuario](user-guide/overview.md)**: Aprende a usar la aplicación paso a paso
- **[Instalación](user-guide/installation.md)**: Guía detallada de instalación y configuración
- **[Primeros Pasos](user-guide/getting-started.md)**: Guía rápida para comenzar a usar la aplicación

### Para Desarrolladores

- **[Arquitectura](architecture/overview.md)**: Comprende la estructura y diseño del sistema
- **[API y Código](api/project-structure.md)**: Documentación detallada de módulos y clases
- **[Desarrollo](development/environment-setup.md)**: Configuración del entorno de desarrollo

### Para Administradores

- **[Despliegue](deployment/pyinstaller.md)**: Guías de empaquetado y distribución
- **[Referencia](reference/dependencies.md)**: Documentación técnica completa

## Conceptos Clave

### Expediente Electrónico
Conjunto de documentos electrónicos correspondientes a un mismo trámite o procedimiento judicial.

### Metadatos
Información estructurada que posibilita la creación, registro, clasificación, acceso, conservación y disposición de los documentos a lo largo del tiempo.

### CUI (Código Único de Identificación)
Código de 23 dígitos que identifica de manera única cada expediente judicial en el sistema.

## Arquitectura Técnica

La aplicación implementa una arquitectura **MVC con patrón Strategy** completamente autónomo:

- **Model**: Lógica de negocio pura (procesamiento, extracción de metadatos, análisis de carpetas)
- **View**: Interfaz gráfica unificada con Tkinter
- **Controller**: Estrategias de procesamiento completamente autónomas

## Soporte y Comunidad

- **GitHub**: [Repositorio oficial](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1)
- **Issues**: [Reportar problemas](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/issues)
- **Twitter**: [@hammerdev99](https://twitter.com/hammerdev99)

## Licencia

Este proyecto está disponible bajo la licencia MIT. Ver [Licencia](reference/license.md) para más detalles.

---

!!! info "Descargo de Responsabilidad"
    Este software se proporciona "tal cual" y el usuario es responsable de su uso. Ver el [descargo completo](reference/license.md#descargo-de-responsabilidades) para más información.