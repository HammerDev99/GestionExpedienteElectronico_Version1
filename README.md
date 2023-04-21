# GestionExpedienteElectronico_Version1

## Tabla de contenidos

- [GestionExpedienteElectronico\_Version1](#gestionexpedienteelectronico_version1)
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
python3 -m venv venv
```

  Para activar el ambiente virtual usa:

```BASH
source venv/bin/activate
```

2. Luego instala las dependencias necesarias:

```BASH
pip install --upgrade -r requirements.txt
```

3. Una vez instalados los modulos, puedes ejecutar el programa:

```BASH
python app_package/main.py
```

4. Por último, debes comprobar que tengas **Microsoft Excel** instalado en tu computador.

---

## Registro de cambios

- 2023-04-12 Start refactoring process
- 2022-12-02 Update folder schema
- 2022-10-26 First release

## Construido con

[Python](https://www.python.org/) versión 3.9.6

## Descargar

Para recibir actualizaciones de las novedades y cambios que se realicen al programa puedes registrar tu correo en el siguiente [formulario](https://forms.gle/kNkKY6zMVfeVUmu18).

Puedes descargar el programa en este [link](https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/published).

---

<a href="https://www.paypal.com/donate/?business=GSEPAASM658FY&no_recurring=0&item_name=Inv%C3%ADtame+a+un+caf%C3%A9.+Contribuyo+a+que+los+humanos+dejen+de+pensar+como+robots+y+piensen+m%C3%A1s+como+humanos+ig:+@daainti&currency_code=USD" target="_blank"><img src="https://ginesrom.es/wp-content/uploads/2021/03/Invitame-a-un-cafe-gines-romero.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;-webkit-box-shadow: 0px 3px 2px 0px rgba(190, 190, 190, 0.5) !important;" ></a>

> La cooperación con los demás constituye la base de la sociedad (extraído de "software libre para una comunidad libre" autor Richard M. Stallman)
