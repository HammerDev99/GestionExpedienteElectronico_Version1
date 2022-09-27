# GestionExpedienteElectronico_Version1

## Tabla de contenidos

- [GestionExpedienteElectronico_Version1](#gestionexpedienteelectronico_version1)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [Descripción](#descripción)
  - [Características de GestionExpedienteElectronico_Version1](#características-de-gestionexpedienteelectronico_version1)
    - [Conceptos](#conceptos)
  - [Uso](#uso)
    - [Instalación](#instalación)
    - [Consideraciones antes de ejecutar](#consideraciones-antes-de-ejecutar)
  - [Construido con](#construido-con)
  - [Autor](#autor)
  - [Licencia](#licencia)
  - [Reporte de fallos](#reporte-de-fallos)
  - [Donaciones](#donaciones)
  - [Descargar archivo .exe (Windows)](#descargar-archivo-exe-windows)

---

## Descripción

Es una aplicación de escritorio que permite realizar de forma automatizada el *diligenciamiento
estricto y actualización* del formato de índice electrónico con los metadatos de los documentos que conforman el expediente electrónico, asimismo permite la creación **desde cero** del índice del expediente electrónico que se encuentra estándarizado en el Plan Estratégico de Transformación Digital de la Rama Judicial, dentro del cual se contempla el programa de Expediente Electrónico. Los parámetros y estándares técnicos y funcionales del presente proyecto, coincide con lo publicado en el acuerdo PCSJA20-11567 de 2020 "Protocolo para la gestión de documentos electrónicos, digitalización y conformación del expediente electrónico" versión 2<!--, el cual consiste en la producción, gestión y tratamiento estandarizado de los documentos y expedientes híbridos y electrónicos-->. Link directo al documento [estándar](https://www.ramajudicial.gov.co/documents/3196516/46103054/Protocolo+para+la+gesti%C3%B3n+de+documentos+electronicos.pdf/cb0d98ef-2844-4570-b12a-5907d76bc1a3).

---

## Características de GestionExpedienteElectronico_Version1

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
<!--
### Pre-requisitos

- Para hacer uso del aplicativo, el usuario deberá descargar en su dispositivo la carpeta del expediente electrónico que requiera gestionar.
- Adicional si se tiene sincronizada la nube en el dispositivo, para evitar errores no deseados deberá pausar la sincronización en la nube.
- Para el buen funcionamiento del aplicativo deberás hacer uso de los siguientes módulos que serán instalados antes de ejecutar el programa:
  - tk==0.1.0
  - openpyxl==3.0.7
  - pandas==1.3.2
  - xlwings==0.24.9
  - pyPDF2==1.26.0
-->
<!-- - Adicional debes de tener instalado el pograma de **Microsoft Excel**. (Validar si es necesario el programa) -->

### Instalación

<!--
Una serie de pasos que se deben ejecutar para tener un entorno de ejecución adecuado:

- Para la instalación de los módulos ([requirements.txt](owl_env/requirements.txt) siendo usuario windows basta con ejecutar el siguiente comando:

    ```cmd
    python -m pip install -r .\requirements.txt
    ```
-->
- No requiere instalación...

### Consideraciones antes de ejecutar

Para el buen funcionamiento del programa deberá seguir los siguientes pasos:

1. Descargar en el equipo una copia de la carpeta que desee gestionar (verificar que no tenga **índice**).
2. Los archivos deben estar en formato pdf, en caso contrario se deberá actualizar manualmente la cantidad de páginas de los archivos en formato .docx (word) dentro del índice electrónico.
3. Antes de ejecutar deberá nombrar los archivos en orden numérico tal cual como desee que se registren en el índice electrónico.
4. Cerrar todos los archivos de excel que tenga en ejecución.
5. Luego de ejecutar el programa GestionExpedienteElectronico_Version1, elegirá la carpeta que contenga los archivos a gestionar con el botón "Agregar carpeta"
6. Deberá confirmar la carpeta elegida.
7. Al finalizar el proceso el sistema arrojará un mensaje que dice "El proceso ha finalizado"

<!--
Para el buen funcionamiento y ejecución de acuerdo con los parámetros establecidos en el "Protocolo de gestión del expediente electrónico" indicado en la descripción de este proyecto, deberá tener en cuenta las siguientes consideraciones:

1. El consecutivo de los archivos debe comprender 4 dígitos (0001Archivo.pdf, 0002Archivo.txt, 0003Archivo.docx)
2. Los archivos y carpetas al interior de la carpeta del expediente electrónico deberán estar nombrados en orden consecutivo (0001Archivo1).
3. Las carpetas que contengan menos de 10 archivos deberán estár incluidos en la carpeta raíz del expediente electrónico
4. Los archivos comprimidos que contengan menos de 10 archivos deberán descomprimirse y ubicarse en la carpeta raíz, de lo contrario se deberá crear una carpeta con el siguiente formato "AnexosMemorialAAAAMMDD" y alojarlos en ella.

---

### Ejecutando el programa

Las siguientes instrucciones te permitirán obtener una ejecución sin errores del programa.

**EN CONSTRUCCIÓN**
-->
---

## Construido con

- [Python](https://www.python.org/) versión 3.9.6

## Autor

- **Daniel Arbelaez** - [HammerDev99](https://github.com/HammerDev99/)

## Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENCIA](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/blob/master/LICENCE) para detalles

<!--
## Expresiones de Gratitud

- Gracias a los creadores de Python y los módulos [tk](https://docs.python.org/3/library/tk.html), [openpyxl](https://openpyxl.readthedocs.io/en/stable/), [pandas](https://pandas.pydata.org/docs/), [xlwings](https://docs.xlwings.org/en/stable/), [pyPDF2](https://pythonhosted.org/PyPDF2/)

---
-->
## Reporte de fallos

Para reporte de fallos se ha dispuesto el siguiente [formulario](https://forms.gle/Rrt2CZbDfodNtn96A)

## Donaciones

[link directo](https://www.paypal.com/donate/?business=GSEPAASM658FY&no_recurring=0&item_name=Su+contribuci%C3%B3n+apoya+el+desarrollo+del+proyecto+%22GestionExpedienteElectronico_Version1%22&currency_code=USD)

## Descargar archivo .exe (Windows)

[link](https://)
