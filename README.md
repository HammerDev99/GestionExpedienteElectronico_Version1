# Agilex (antes GestionExpedienteElectronico)

## Tabla de contenidos

- [Agilex (antes GestionExpedienteElectronico)](#agilex-antes-gestionexpedienteelectronico)
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

![alt](src/assets/Demo.gif)

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
    python src/__main__.py
    ```

4. Por último, debes comprobar que tengas **Microsoft Excel** instalado en tu computador.

---

## Registro de cambios

La versión actual es **1.5.2**. El historial completo de versiones está en
[CHANGELOG.md](CHANGELOG.md), y también disponible en la
[documentación oficial](https://docs.agilex.sprintjudicial.com/reference/changelog/).

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
