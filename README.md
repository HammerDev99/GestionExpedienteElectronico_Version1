# GestionExpedienteElectronico

## Tabla de contenidos

- [GestionExpedienteElectronico](#gestionexpedienteelectronico)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Descripción](#descripción)
  - [Demo](#demo)
  - [Características de GestionExpedienteElectronico\_Version1](#características-de-gestionexpedienteelectronico_version1)
    - [Conceptos](#conceptos)
  - [Instalación](#instalación)
    - [GitHub](#github)
      - [Obtener copia del repositorio](#obtener-copia-del-repositorio)
      - [Preparar y ejecutar](#preparar-y-ejecutar)
  - [Registro de cambios](#registro-de-cambios)
  - [Construido con](#construido-con)
  - [Descargar](#descargar)
  - [Descargo de responsabilidades](#descargo-de-responsabilidades)

---

## Descripción

Se trata de una solución RDA (Robotic Desktop Automation versión Beta) que permite realizar de forma automatizada la *creación y diligenciamiento* del formato índice electrónico con los metadatos de los archivos alojados en una carpeta específica; aquellos archivos (documentos) conformarán un expediente electrónico y mediante este software se creará **desde cero** el índice del mismo. Dicho procedimiento se encuentra estándarizado en el Plan Estratégico de Transformación Digital de la Rama Judicial, dentro del cual se contempla el programa de Expediente Electrónico. El presente proyecto se amolda en mayor medida a los parámetros, estándares técnicos y funcionales del acuerdo PCSJA20-11567 de 2020 "Protocolo para la gestión de documentos electrónicos, digitalización y conformación del expediente electrónico" Versión 2. [Link directo al Protocolo](https://www.ramajudicial.gov.co/documents/3196516/46103054/Protocolo+para+la+gesti%C3%B3n+de+documentos+electronicos.pdf/cb0d98ef-2844-4570-b12a-5907d76bc1a3).

## Demo

![alt](assets/Demo.gif)

## Características de GestionExpedienteElectronico_Version1

Este proyecto fue desarrollado para gestionar una función específica de caracter administrativo, asistiendo los procedimientos que haría un empleado de forma manual mediante una aplicación de forma automatizada.

### Conceptos

**Expediente Electrónico**: Conjunto de documentos electrónicos correspondientes a un mismo trámite o procedimiento judicial.

**Metadatos**: Información estructurada o semi estructurada que posibilita la creación, registro, clasificación, acceso, conservación y disposición de los documentos a lo **largo del tiempo**.

> Los metadatos incluyen una amplia información que se puede utilizar para identificar, autenticar y contextualizar los documentos, los procesos y sus relaciones.

**Metadatos de los documentos**: Describen la información de cada uno de los documentos que conforman el expediente, para asegurar la integridad, fiabilidad, disponibilidad y **valor probatorio de los documentos**. Algunos de los metadatos de los documentos que se registran en el libro índice son:

- Nombre Documento
- Fecha creación del documento
- Fecha Incorporación Expediente
- Orden Documento
- Número de Páginas
- Página Inicio (automático con fórmula excel)
- Página Fin (automático con fórmula excel)
- Formato
- Tamaño
- Origen (Electrónico ó Digitalizado)
- Observaciones

---

## Instalación

### GitHub

#### Obtener copia del repositorio

1. Descargalo directamente a tu computador o ejecuta el siguiente comando en la terminal para clonar el repositorio de GitHub en tu equipo:
  
```BASH
git clone https://github.com/HammerDev99/GestionExpedienteElectronico_Version1.git
```
  
2. Navega hacia el directorio del repositorio que acabas de clonar:

```BASH
cd GestionExpedienteElectronico_Version1
```

3. Ahora, debes vincular tu repositorio local con el repositorio del fork que quieres hacer en tu cuenta de GitHub. Para ello, ejecuta el siguiente comando:

```BASH
git remote add fork https://github.com/tu-nombre-de-usuario/GestionExpedienteElectronico_Version1.git
```

Sustituye "tu-nombre-de-usuario" por el usuario que llevas en github.

4. Luego, ejecuta el siguiente comando para enviar todos los cambios del repositorio local al repositorio del fork en tu cuenta de GitHub:

```Bash
git push fork master
```

Con estos pasos, deberías haber creado un fork del repositorio original en tu cuenta de GitHub. Recuerda que un fork es una copia del repositorio original que puedes usar para hacer cambios sin afectar el repositorio original. Puedes enviar tus cambios de vuelta al repositorio original a través de un "pull request".

#### Preparar y ejecutar

1. Para preparar el programa con buenas prácticas debes de crear el ambiente virtual con el siguiente comando:

```BASH
python -m venv .venv
```

  Para activar el ambiente virtual usa:

```BASH
#WINDOWS
.venv\Scripts\Activate
```

2. Luego instala las dependencias necesarias:

```BASH
pip install --upgrade -r requirements.txt
```

3. Una vez instalados los modulos, puedes ejecutar el programa:

```BASH
python main.py
```

4. Por último, debes comprobar que tengas **Microsoft Excel** instalado en tu computador.

---

## Registro de cambios

- 2024-11-15 Nuevo Release 🚀 GestionExpedienteElectronico v1.4.0
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

## Construido con

[Python](https://www.python.org/) versión 3.9.6

## Descargar

[Descargar última versión](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/latest)

Para recibir actualizaciones de las novedades y cambios que se realicen al programa puedes seguirme en la cuenta de twitter [@hammerdev99](https://www.twitter.com/hammerdev99) dónde se comparte su creación en público.

## Descargo de responsabilidades

Este documento tiene por objeto informar a los usuarios del software GestionExpedienteElectronico_Version1 sobre las condiciones y limitaciones en el uso de la aplicación. El uso de este software implica la aceptación de los términos y condiciones establecidos a continuación:

1. El software GestionExpedienteElectronico_Version1 fue desarrollado para solucionar una necesidad personal del creador y puede ser utilizado por otras personas bajo su propia responsabilidad.

2. El uso del software GestionExpedienteElectronico_Version1 es responsabilidad exclusiva del usuario. El creador no se hace responsable de cualquier daño, pérdida o perjuicio que pudiera derivarse del uso de la aplicación.

3. El software GestionExpedienteElectronico_Version1 se proporciona "tal cual" y sin garantías de ningún tipo, ya sean explícitas o implícitas. El creador no garantiza la precisión, fiabilidad, integridad o calidad de la aplicación ni de cualquier información o contenido relacionado.

4. El usuario es el único responsable de la selección, instalación, uso y resultados obtenidos del software GestionExpedienteElectronico_Version1. El creador no será responsable de ningún error, virus, interrupción del servicio, pérdida de datos, pérdida de ingresos o cualquier otro daño que pudiera resultar del uso del software.

5. El usuario acepta indemnizar y eximir de responsabilidad al creador por cualquier reclamo, demanda o daño, incluyendo honorarios razonables de abogados, que pudiera surgir de la utilización del software GestionExpedienteElectronico_Version1.

6. El creador se reserva el derecho de modificar, suspender o descontinuar el software GestionExpedienteElectronico_Version1 en cualquier momento y sin previo aviso.

7. Al descargar, instalar o utilizar el software GestionExpedienteElectronico_Version1, el usuario acepta y reconoce haber leído y entendido este documento y acepta los términos y condiciones establecidos.

---

> La cooperación con los demás constituye la base de la sociedad (extraído de "software libre para una comunidad libre" autor Richard M. Stallman)
