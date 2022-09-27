# GestionExpedienteElectronico_Version1

## (README EN CONSTRUCCIÓN)

## Tabla de contenidos

- [GestionExpedienteElectronico_Version1](#gestionexpedienteelectronico_version1)
  - [(README EN CONSTRUCCIÓN)](#readme-en-construcción)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Descripción](#descripción)
  - [Características de GestionExpedienteElectronico](#características-de-gestionexpedienteelectronico)
    - [Conceptos](#conceptos)
  - [Uso](#uso)
    - [Pre-requisitos](#pre-requisitos)
    - [Instalación](#instalación)
    - [Consideraciones antes de ejecutar](#consideraciones-antes-de-ejecutar)
    - [Ejecutando el programa](#ejecutando-el-programa)
  - [Construido con](#construido-con)
  - [Autor](#autor)
  - [Licencia](#licencia)
  - [Expresiones de Gratitud](#expresiones-de-gratitud)
  - [Reporte de fallos](#reporte-de-fallos)

---

## Descripción

Es una aplicación de escritorio que permite realizar de forma automatizada el *diligenciamiento
estricto y actualización* del formato de índice electrónico con los metadatos de los documentos que conforman el expediente electrónico, asimismo permite la creación desde cero del índice del expediente electrónico que se encuentra estándarizado y regulado en el Plan Estratégico de Transformación Digital de la Rama Judicial, dentro del cual se contempla el programa de Expediente Electrónico. Los parámetros y estándares técnicos y funcionales del presente proyecto, coincide con lo indicado en el acuerdo PCSJA20-11567 de 2020 "Protocolo para la gestión de documentos electrónicos, digitalización y conformación del expediente electrónico" versión 2, el cual consiste en la producción, gestión y tratamiento estandarizado de los documentos y expedientes híbridos y electrónicos. Al documento estándar se puede acceder mediante el siguiente [link](https://www.ramajudicial.gov.co/documents/3196516/46103054/Protocolo+para+la+gesti%C3%B3n+de+documentos+electronicos.pdf/cb0d98ef-2844-4570-b12a-5907d76bc1a3).

---

## Características de GestionExpedienteElectronico

Esta aplicación de escritorio fue desarrollada para gestionar de forma automatizada el expediente electrónico y realizar los procedimientos que haría un empleado de forma manual.

### Conceptos

**Expediente Electrónico**: Conjunto de documentos electrónicos correspondientes a un mismo trámite o procedimiento, cualquiera que sea el tipo de información que contengan.

**Metadatos**: Información estructurada o semi estructurada que posibilita la creación, registro, clasificación, acceso, conservación y disposición de los documentos a lo largo del tiempo. Los metadatos incluyen una amplia información que se puede utilizar para identificar, autenticar y contextualizar los documentos, los procesos y sus relaciones. Los metadatos permiten asegurar la integridad, fiabilidad, disponibilidad y valor probatorio de los documentos.

**Metadatos de los documentos**: Describen la información de cada uno de los documentos que conforman el expediente, para asegurar su secuencialidad, integridad y disponibilidad. Algunos de los metadatos de los documentos que se registran en el libro índice son:

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

## Uso

### Pre-requisitos

- Para hacer uso del aplicativo, el usuario deberá descargar en su dispositivo la carpeta del expediente electrónico que requiera gestionar.
- Adicional si se tiene sincronizada la nube en el dispositivo, para evitar errores no deseados deberá pausar la sincronización en la nube.
- Para el buen funcionamiento del aplicativo deberás hacer uso de los siguientes módulos que serán instalados antes de ejecutar el programa:
  - tk==0.1.0
  - openpyxl==3.0.7
  - pandas==1.3.2
  - xlwings==0.24.9
  - pyPDF2==1.26.0

<!-- - Adicional debes de tener instalado el pograma de **Microsoft Excel**. (Validar si es necesario el programa) -->

### Instalación

Una serie de pasos que se deben ejecutar para tener un entorno de ejecución adecuado:

- Para la instalación de los módulos ([requirements.txt](owl_env/requirements.txt) siendo usuario windows basta con ejecutar el siguiente comando:

    ```cmd
    python -m pip install -r .\requirements.txt
    ```

- Instalar...

### Consideraciones antes de ejecutar

Para el buen funcionamiento y ejecución de acuerdo con los parámetros establecidos en el "Protocolo de gestión del expediente electrónico" indicado en la descripción de este proyecto, deberá tener en cuenta las siguientes consideraciones:

1. El consecutivo de los archivos debe comprender 4 dígitos (0001Archivo.pdf, 0002Archivo.txt, 0003Archivo.docx)
2. Los archivos y carpetas al interior de la carpeta del expediente electrónico deberán estar nombrados en orden consecutivo (0001Archivo1).
3. Las carpetas que contengan menos de 10 archivos deberán estár incluidos en la carpeta raíz del expediente electrónico
4. Los archivos comprimidos que contengan menos de 10 archivos deberán descomprimirse y ubicarse en la carpeta raíz, de lo contrario se deberá crear una carpeta con el siguiente formato "AnexosMemorialAAAAMMDD" y alojarlos en ella.

---

### Ejecutando el programa

Las siguientes instrucciones te permitirán obtener una ejecución sin errores del programa.

**EN CONSTRUCCIÓN**

---

## Construido con

- [Python](https://www.python.org/) versión 3.9.6 - El lenguaje de programación usado

---

## Autor

- **Daniel Arbelaez** - *Trabajo Inicial* - [HammerDev99](https://github.com/HammerDev99/)

---

## Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENCIA](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/blob/master/LICENCE) para detalles

---

## Expresiones de Gratitud

- Gracias a los creadores de Python y los módulos [tk](https://docs.python.org/3/library/tk.html), [openpyxl](https://openpyxl.readthedocs.io/en/stable/), [pandas](https://pandas.pydata.org/docs/), [xlwings](https://docs.xlwings.org/en/stable/), [pyPDF2](https://pythonhosted.org/PyPDF2/)

---

## Reporte de fallos

Para reporte de fallos se ha dispuesto el siguiente [formulario](https://forms.gle/Rrt2CZbDfodNtn96A) donde podrá registrar la evidencia de forma detallada

## Donaciones

[link directo](https://www.paypal.com/donate/?business=GSEPAASM658FY&no_recurring=0&item_name=Su+contribuci%C3%B3n+apoya+el+desarrollo+del+proyecto+%22owl_system%22&currency_code=USD)

## Descargar archivo .exe

[link]()
