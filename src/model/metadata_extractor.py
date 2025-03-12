# coding=utf-8

import datetime
import re
import os
import string
import random
import win32com.client as win32
import logging
from PyPDF2 import PdfReader


class MetadataExtractor:

    # Constantes de clase
    DOCUMENTO_ELECTRONICO = "Documento electronico"
    DOCUMENTO_ELECTRONICO_DEFAULT = "DocumentoElectronico"
    CARPETA_TYPE = "Carpeta"
    MAX_LENGTH = 36
    MAX_NAME_LENGTH = 40

    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger("metadata_extractor")

    def get_metadata(self, files):
        """
        Extrae metadatos de una lista de archivos.
        Args:
            files (List[str]): Lista de rutas de archivos.
        Returns:
            Tuple[List[str], List[str], List[str], List[str]]:
            - fechamod: Lista de fechas de modificación como cadenas.
            - tama: Lista de tamaños de archivos convertidos a unidades legibles.
            - cantidadpag: Lista de conteos de páginas.
            - observaciones: Lista de observaciones o comentarios.
        Modules:
            - datetime: Usado para manejar fechas.
            - os: Usado para operaciones del sistema de archivos.
        """

        fechamod = []
        tama = []
        cantidadpag = []
        observaciones = []
        for x in files:
            if os.path.isfile(x):
                fechamod.append(str(datetime.date.fromtimestamp(os.path.getmtime(x))))
                tama.append(self.size_units_converter(os.path.getsize(x)))
                cantidadpag.append(self.page_counter(x))
                observaciones.append("")
            else:
                # Si es carpeta o anexo masivo
                fechamod.append(str(datetime.date.fromtimestamp(os.path.getmtime(x))))
                tama.append("-")
                cantidadpag.append("1")
                list_files = os.listdir(x)
                _, extensiones = self.separate_path(list_files)
                
                # Reemplazar extensiones vacías con "carpeta" para subcarpetas
                for i, file in enumerate(list_files):
                    if os.path.isdir(os.path.join(x, file)) and extensiones[i] == "":
                        extensiones[i] = "carpeta"
                
                comments = dict(
                    zip(extensiones, map(lambda x: extensiones.count(x), extensiones))
                )
                nombres_extensiones, _, _, _, _, _ = self.format_names(x, list_files)
                self.rename_files(list_files, nombres_extensiones, x)
                observaciones.append("Archivos contenidos: " + str(comments))
        return fechamod, tama, cantidadpag, observaciones

    @staticmethod
    def separate_path(files):
        """
        Separa los nombres de archivo y sus extensiones de una lista de rutas de archivos.
        Args:
            files (List[str]): Una lista de rutas de archivos.
        Returns:
            Tuple[List[str], List[str]]: Dos listas, una que contiene los nombres de archivo sin extensiones, y la otra que contiene las extensiones de archivo.
        Modules:
            os: Esta función utiliza el módulo os para dividir las rutas de archivo.
        """

        nombres = []
        extensiones = []
        for x in files:
            nombres.append(os.path.splitext(x)[0])
            extensiones.append(os.path.splitext(x)[1])
        return nombres, extensiones

    # Función duplicada
    def rename_files(self, files, nombres_extensiones, ruta):
        """
        Renombra una lista de archivos a nuevos nombres proporcionados en `nombres_extensiones`. Si un archivo no existe,
        agrega una cadena aleatoria al nuevo nombre.
        Args:
            files (list): Lista de nombres de archivos a renombrar.
            nombres_extensiones (list): Lista de nuevos nombres de archivos con extensiones.
            ruta (str): Ruta del directorio donde se encuentran los archivos.
        Modules:
            os
        Raises:
            Exception: Si ocurre un error durante el renombrado, se captura una excepción y se imprime un mensaje.
        """

        for i in range(len(files)):
            fulldirct = os.path.join(ruta, files[i])
            if os.path.exists(fulldirct):
                os.rename(fulldirct, os.path.join(ruta, nombres_extensiones[i]))
            else:
                try:
                    length_of_string = 3
                    os.rename(
                        ruta + chr(92) + files[i],
                        ruta
                        + chr(92)
                        + os.path.splitext(nombres_extensiones[i])[0]
                        + "".join(
                            random.choice(string.ascii_letters + string.digits)
                            for _ in range(length_of_string)
                        )
                        + os.path.splitext(nombres_extensiones[i])[1],
                    )
                except Exception as e:
                    self.logger.exception(
                        "Excepcion presentada intentando el renombrado archivos"
                        + str(e)
                    )

    def format_names(self, ruta, files):
        """
        Formatea los nombres de archivos y directorios en una ruta dada.
        Args:
            ruta (str): La ruta al directorio que contiene los archivos.
            files (list): Lista de nombres de archivos y directorios a procesar.
        Returns:
            tuple: (nombres_extensiones, nombres, extensiones, numeraciones, ban, nombres_indice)
        """
        nombres_indice = self.procesa_cadena_indice(files)
        nombres, extensiones = self._extraer_nombres_extensiones(ruta, files)
        nombres = self._formatear_nombres(nombres, nombres_indice)
        nombres_extensiones = self._generar_nombres_finales(nombres, extensiones)
        numeraciones = self._generar_numeraciones(len(nombres))
        ban = self._verificar_orden(files, nombres_extensiones)

        return (
            nombres_extensiones,
            nombres,
            extensiones,
            numeraciones,
            ban,
            nombres_indice,
        )

    def _extraer_nombres_extensiones(self, ruta, files):
        """Extrae nombres y extensiones de los archivos."""
        nombres = []
        extensiones = []

        for archivo in files:
            nombre, extension = self._obtener_nombre_extension(ruta, archivo)
            nombres.append(nombre)
            extensiones.append(extension)

        return nombres, extensiones

    def _obtener_nombre_extension(self, ruta, archivo):
        """Obtiene el nombre y extensión de un archivo individual."""
        ruta_completa = os.path.join(ruta, archivo)
        if os.path.isfile(ruta_completa):
            return os.path.splitext(archivo)
        return archivo, self.CARPETA_TYPE

    def _formatear_nombres(self, nombres, nombres_indice):
        """Formatea la lista de nombres según las reglas establecidas."""
        return [
            self._formatear_nombre_individual(nombre, nombres_indice[i], i)
            for i, nombre in enumerate(nombres)
        ]

    def _formatear_nombre_individual(self, nombre, nombre_indice, indice):
        """Formatea un nombre individual aplicando todas las reglas."""
        nombre_procesado = self._limpiar_caracteres(nombre)
        nombre_procesado = self._aplicar_nombre_por_defecto(
            nombre_procesado, nombre_indice
        )
        return f"{indice+1:03}{nombre_procesado}"

    def _limpiar_caracteres(self, nombre):
        """Limpia y normaliza un nombre según las reglas establecidas."""
        if self._requiere_limpieza(nombre):
            nombre = self._aplicar_formato_basico(nombre)
        nombre = self._eliminar_numeros_iniciales(nombre)
        return nombre[: self.MAX_LENGTH]

    def _requiere_limpieza(self, nombre):
        """Determina si un nombre requiere limpieza."""
        return not nombre.isalnum() or len(nombre) > self.MAX_NAME_LENGTH

    def _aplicar_formato_basico(self, nombre):
        """Aplica el formato básico al nombre."""
        nombre = string.capwords(nombre)
        return re.sub("[^a-zA-Z0-9]+", "", nombre)

    def _eliminar_numeros_iniciales(self, nombre):
        """Elimina los números iniciales del nombre."""
        for i, char in enumerate(nombre):
            if char.isalpha():
                return nombre[i:]
        return nombre

    def _aplicar_nombre_por_defecto(self, nombre, nombre_indice):
        """Aplica el nombre por defecto si es necesario."""
        if nombre_indice == self.DOCUMENTO_ELECTRONICO or not nombre:
            return self.DOCUMENTO_ELECTRONICO_DEFAULT
        return nombre

    def _generar_nombres_finales(self, nombres, extensiones):
        """Genera los nombres finales combinando nombres y extensiones."""
        return [
            f"{nombre}{extension}" if extension != self.CARPETA_TYPE else nombre
            for nombre, extension in zip(nombres, extensiones)
        ]

    def _generar_numeraciones(self, cantidad):
        """Genera la lista de numeraciones."""
        return list(range(1, cantidad + 1))

    def _verificar_orden(self, files, nombres_extensiones):
        """Verifica si los archivos están en orden."""
        return self.is_order_correct(files, nombres_extensiones)

    def procesa_cadena_indice(self, files):
        """
        Procesa una lista de nombres de archivos para extraer y formatear las palabras.

        Args:
            files (List[str]): Lista de nombres de archivos.

        Returns:
            List[str]: Lista de cadenas formateadas.

        Modules:
            os, re, random, string

        Functionality:
            - Separa el nombre de la extensión.
            - Extrae las palabras utilizando expresiones regulares.
            - Capitaliza la primera palabra y convierte las demás a minúscula.
            - Si la cadena resultante es un número, agrega un carácter aleatorio al inicio.
            - Si la cadena está vacía, asigna "Documento electronico".
        """

        lista_cadena = list(files)
        for i in range(len(lista_cadena)):
            cadena = lista_cadena[i]
            if " " in cadena:
                cadena = os.path.splitext(cadena)[0]  # Separa el nombre de la extensión
                palabras = re.findall(
                    r"[A-Za-z]+", cadena
                )  # Aplicar expresión regular para extraer las palabras
                resultado = " ".join(
                    palabras
                )  # Unir las palabras en una sola cadena con espacios entre ellas
            else:
                palabras = re.findall(
                    "[A-Z][a-z]*", cadena
                )  # Encuentra las palabras en la cadena que comienzan con una letra mayúscula seguida de letras minúsculas
                resultado = " ".join(
                    palabras
                )  # Une las palabras con espacios para formar la cadena resultante

            palabras = resultado.split()  # Dividir la cadena en palabras
            if palabras:
                # Capitalizar la primera palabra
                palabras[0] = palabras[0].capitalize()
                # Convertir las demás palabras a minúscula
                palabras[1:] = [palabra.lower() for palabra in palabras[1:]]
            resultado = " ".join(palabras)  # Unir las palabras en una cadena nuevamente

            if resultado.isdigit():
                caracter_aleatorio = random.choice(string.ascii_letters)
                resultado = caracter_aleatorio + resultado

            if resultado == "":
                resultado = self.DOCUMENTO_ELECTRONICO

            # SE OMITE ESTA CONDICION PORQUE PUEDE ESTAR PROVOCANDO ERRORES EN EL PROCESO DE MIGRACION
            # if len(resultado) > 36:
            #    resultado = resultado[:36]

            lista_cadena[i] = resultado  # Modificar la cadena de la lista
        return lista_cadena

    def is_order_correct(self, files, nombres_extensiones):
        """
        Verifica el orden de los archivos consecutivos.
        Args:
            files (List): Lista de nombres de archivos.
            nombres_extensiones (List): Lista de nombres de archivos esperados con extensiones.
        Returns:
            bool: True si el orden es incorrecto, False en caso contrario.
        """

        cont = 0
        for i in files:
            for j in nombres_extensiones:
                if i != j:
                    cont = cont + 1
        if cont != 0:
            return True
        else:
            return False

    def size_units_converter(self, size):
        """
        Convierte el tamaño del archivo de bytes a una cadena legible con las unidades apropiadas.
        Args:
            size (int): El tamaño del archivo en bytes.
        Returns:
            str: Una cadena que representa el tamaño en las unidades apropiadas (BYTES, KB, MB, GB, TB).
        Notes:
            - La función convierte el tamaño a la unidad más grande posible sin exceder el tamaño dado.
            - Si el tamaño es 0, devuelve "0 BYTES".
        """

        kb = 1024
        file_size_bytes = kb / 1024
        mb = kb * 1024
        gb = mb * 1024
        tb = gb * 1024
        if size >= tb:
            return "%.1f TB" % float(size / tb)
        if size >= gb:
            return "%.1f GB" % float(size / gb)
        if size >= mb:
            return "%.1f MB" % float(size / mb)
        if size >= kb:
            return "%.1f KB" % float(size / kb)
        if size < kb:
            return "%.0f BYTES" % float(size / file_size_bytes)
        if size == 0:
            return "0 BYTES"

    def page_counter(self, file):
        """
        Cuenta el número de páginas en un archivo dado.
        Parámetros:
            file (str): La ruta al archivo cuyas páginas se van a contar.
        Returns:
            int: El número de páginas en el archivo. Devuelve 0 si el tipo de archivo no es compatible o si ocurre un error.
        Módulos:
            PyPDF2, warnings, os, sys
        Tipos de archivos compatibles:
            - PDF (.pdf)
            - Documentos de Word (.docx, .doc)
            - Hojas de cálculo de Excel (.xls, .xlsx, .xlsm)
            - Archivos de imagen (.bmp, .jpeg, .jpg, .png, .tif, .gif)
            - Archivos de video (.mp4, .wmv)
            - Archivos de texto (.txt, .textclipping)
            - Archivos de correo electrónico (.eml)
            - Archivos HTML (.html)
        """

        _path, extension = os.path.splitext(file)
        extension = extension.lower()
        if os.path.isfile(file):
            if extension == ".pdf":
                try:
                    pdf_path = file
                    total_pages = count_pages_in_pdf(self, pdf_path)
                    return total_pages
                except Exception:
                    return 0
            elif extension == ".docx" or extension == ".doc":
                try:
                    docx_path = file
                    total_pages = count_pages_in_docx(self, docx_path)
                    return total_pages
                except Exception:
                    return 0
            elif (
                extension == ".xls"
                or extension == ".xlsx"
                or extension == ".xlsm"
                or extension == ".bmp"
                or extension == ".jpeg"
                or extension == ".jpg"
                or extension == ".mp4"
                or extension == ".png"
                or extension == ".tif"
                or extension == ".textclipping"
                or extension == ".wmv"
                or extension == ".eml"
                or extension == ".txt"
                or extension == ".gif"
                or extension == ".html"
            ):
                return 1
            else:
                return 0
        else:
            return 1


def count_pages_in_pdf(self, pdf_path):
    """
    Cuenta el número de páginas en un archivo PDF utilizando dos métodos diferentes.
    Args:
        pdf_path (str): Ruta al archivo PDF.
    Returns:
        int: Número de páginas en el documento. Devuelve 0 si ocurre un error.
    Métodos:
        - PyPDF2.PdfFileReader: Intenta contar las páginas utilizando PdfFileReader de PyPDF2.
        - PyPDF2.PdfReader: Intenta contar las páginas utilizando PdfReader de PyPDF2.
    Excepciones:
        - Imprime un mensaje de error si falla el conteo de páginas en cualquiera de los métodos.
    """

    """ # Primer método: PyPDF2.PdfFileReader (NO FUNCIONÓ CON ARCHIVOS PDF PROTEGIDOS)
    try:
        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfFileReader(f)
            if not sys.warnoptions:
                warnings.simplefilter("ignore")
            return pdf.getNumPages()
    except Exception as e:
        self.logger.exception(f"Error al contar páginas con PyPDF2.PdfFileReader: {e}") """

    # Segundo método: PyPDF2.PdfReader
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        self.logger.exception(f"Error al contar páginas con PyPDF2.PdfReader: {e}")
        return 0


def count_pages_in_docx(self, doc_path):
    """
    Cuenta el número de páginas en un archivo .doc o .docx utilizando Microsoft Word.
    Args:
        doc_path (str): Ruta al archivo .doc o .docx.
    Returns:
        int: Número de páginas en el documento.
    Raises:
        Exception: Si hay un error al abrir o procesar el documento.
    """
    try:
        # Inicia Microsoft Word
        word = win32.Dispatch("Word.Application")
        word.Visible = False  # No mostrar la ventana de Word

        # Abre el documento .doc o .docx
        doc = word.Documents.Open(doc_path)

        # Recalcula las páginas
        doc.Repaginate()  # Asegura que las páginas se recalculen si es necesario

        # Obtiene el número de páginas
        pages = doc.ComputeStatistics(
            2
        )  # 2 es el código para contar páginas (wdStatisticPages)

        # Cierra el documento y Word
        doc.Close(False)  # False para no guardar cambios
        word.Quit()

        return pages
    except Exception as e:
        self.logger.exception(f"Error al contar páginas en el archivo {doc_path}: {e}")
        return 0
