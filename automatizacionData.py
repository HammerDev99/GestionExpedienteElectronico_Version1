import datetime
import re
import os
import string
import sys
import warnings
import PyPDF2
import random  # importado por función duplicada
import win32com.client as win32


class AutomatizacionData:

    def __init__(self):
        pass

    def getMetadata(self, files):
        """
        @param: files (List)
        @return: fechamod, tama, cantidadpag, observaciones (List)
        @modules: datetime, os
        """

        fechamod = []
        tama = []
        cantidadpag = []
        observaciones = []
        for x in files:
            if os.path.isfile(x):
                fechamod.append(str(datetime.date.fromtimestamp(os.path.getmtime(x))))
                tama.append(self.sizeUnitsConverter(os.path.getsize(x)))
                cantidadpag.append(self.pageCounter(x))
                observaciones.append("")
            else:
                fechamod.append(str(datetime.date.fromtimestamp(os.path.getmtime(x))))
                tama.append("-")
                cantidadpag.append("1")
                list_files = os.listdir(x)
                nombres, extensiones = self.separatePath(list_files)
                comments = dict(
                    zip(extensiones, map(lambda x: extensiones.count(x), extensiones))
                )  # combinar los valores para posteriormente pasarlo a un diccionario. Utilizamos map() y le aplicamos una lambda esta lambda obtendrá la veces que se repite un valor, esto para cada valer de la lista. Luego se utiliza zip() para mezclar ambos datos y obtener una tapa para posteriormente pasarlo a un diccionario.
                nombresExtensiones, nombres, extensionesR, numeraciones, ban = (
                    self.formatNames(x, list_files)
                )
                self.renameFiles(list_files, nombresExtensiones, x)
                observaciones.append("Archivos contenidos: " + str(comments))
        return fechamod, tama, cantidadpag, observaciones

    def set_comments_folder(self, extensiones):
        """
        @param: extensiones (List)
        @return: resultado (Dict)
        @modules: None
        """
        resultado = dict(
            zip(extensiones, map(lambda x: extensiones.count(x), extensiones))
        )

        return resultado
        """ conteo=Counter(extensiones)

        resultado={}
        for clave in conteo:  
            valor = conteo[clave]
            if valor != 1:
                resultado[clave] = valor
        return(resultado) """

    """ ************ """

    # Función duplicada
    def separatePath(self, files):
        """
        @param: files (List)
        @return: nombres, extensiones ambos de tipo List
        @modules: os
        """

        nombres = []
        extensiones = []
        for x in files:
            nombres.append(os.path.splitext(x)[0])
            extensiones.append(os.path.splitext(x)[1])
        return nombres, extensiones

    # Función duplicada
    def renameFiles(self, files, nombresExtensiones, ruta):
        """
        @param: files, nombresExtensiones (List), ruta (string)
        @modules: os
        """

        for i in range(len(files)):
            fulldirct = os.path.join(ruta, files[i])
            if os.path.exists(fulldirct):
                os.rename(fulldirct, os.path.join(ruta, nombresExtensiones[i]))
            else:
                try:
                    # number_of_strings = 3
                    length_of_string = 3
                    os.rename(
                        ruta + chr(92) + files[i],
                        ruta
                        + chr(92)
                        + os.path.splitext(nombresExtensiones[i])[0]
                        + "".join(
                            random.choice(string.ascii_letters + string.digits)
                            for _ in range(length_of_string)
                        )
                        + os.path.splitext(nombresExtensiones[i])[1],
                    )
                except:
                    print("Excepcion presentada: \n")

    """ ************ """

    # Separar función en funciones más pequeñas
    """ La solucion más efectiva es crear una funcion principal que cuente con un ciclo y envie cada nombre de archivo llamando a otra funcion que luego controle cada palabra del nombre del archivo y así gestionar hasta el detalle más mínimo  """

    def formatNames(self, ruta, files):
        """
        @param: ruta, files
        @return: nombresExtensiones, nombres, extensiones, numeraciones, ban, nombres_indice
        @modules: re, os, string

        - Separa el nombre y la extension, validando si es carpeta
        - Asigna 'Carpeta' en extension del archivo
        - Aplica mayuscula a la primera letra de cada palabra
        - Elimina caracteres menos a-zA-Z0-9
        - Elimina los numeros primeros existentes del nombre
        - Limita la cantidad de caracteres a 36
        - En caso de estar vacio asigna el nombre DocumentoElectronico
        - Crea consecutivos
        - Agrega consecutivo al comienzo del nombre en el mismo orden de la carpeta
        - Valida con isorderCorrect si los archivos estan en orden, en caso negativo ban = true
        """

        # Función para procesar nombres del índice
        nombres_indice = []
        nombres_indice = self.procesa_cadena_indice(files)

        nombres = []
        extensiones = []
        for x in files:
            fulldirct = os.path.join(ruta, x)
            if os.path.isfile(fulldirct):
                nombres.append(os.path.splitext(x)[0])
                extensiones.append(os.path.splitext(x)[1])
            else:
                nombres.append(x)
                extensiones.append("Carpeta")

        ban = False
        for x in range(len(nombres)):
            if not (nombres[x].isalnum()) or len(nombres[x]) > 40:
                nombres[x] = string.capwords(nombres[x])
                result = re.sub("[^a-zA-Z0-9]+", "", nombres[x])
                nombres[x] = result
                ban = True
            else:
                # Entran los archivos sin extensión
                # print("entró: ",nombres[x])
                pass
            cont = 0
            for caracter in nombres[x]:
                if caracter.isalpha():
                    nombres[x] = nombres[x][cont:]
                    break
                else:
                    if caracter.isnumeric():
                        cont = cont + 1
                        continue
            nombres[x] = nombres[x][0:36]
            # Compara valores de nombre_indice y nombres para aplicar nombre a archivo
            if (nombres_indice[x] == "Documento electronico") or (nombres[x] == ""):
                nombres[x] = "DocumentoElectronico"

            nombres[x] = str(f"{x+1:03}") + nombres[x]

        nombresExtensiones = []
        for x in range(len(nombres)):
            if extensiones[x] != "Carpeta":
                nombresExtensiones.append(str(nombres[x]) + str(extensiones[x]))
            else:
                nombresExtensiones.append(str(nombres[x]))
        numeraciones = list(range(len(nombres) + 1))
        numeraciones.pop(0)

        if self.isOrderCorrect(files, nombresExtensiones):
            ban = True

        return (
            nombresExtensiones,
            nombres,
            extensiones,
            numeraciones,
            ban,
            nombres_indice,
        )

    def procesa_cadena_indice(self, files):
        """
        @param: files (List)
        @return: lista_cadena (List)
        @modules: os, re, random, string

        - La función toma una lista de nombres de archivos, los procesa para extraer y formatear las palabras, y devuelve una lista de cadenas formateadas
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
                resultado = "Documento electronico"

            lista_cadena[i] = resultado  # Modificar la cadena de la lista
        return lista_cadena

    def isOrderCorrect(self, files, nombresExtensiones):
        """
        @param: files (List), nombresExtensiones (List)
        @return: Bool
        @modules: None

        - Verifica el orden de los consecutivos de los archivos
        """

        cont = 0
        for i in files:
            for j in nombresExtensiones:
                if i != j:
                    cont = cont + 1
        if cont != 0:
            return True
        else:
            return False

    def sizeUnitsConverter(self, size):
        """
        @param: size (int); tamaño del archivo en bytes
        @return: string; contiene cantidad más unidad de medición
        @modules: None
        """

        kb = 1024
        bytes = kb / 1024
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
            return "%.0f BYTES" % float(size / bytes)
        if size == 0:
            return "0 BYTES"

    def pageCounter(self, file):
        """
        @param: file (string)
        @return: int; cantidad de paginas
        @modules: PyPDF2, warnings, os, sys
        """

        path, extension = os.path.splitext(file)
        extension = extension.lower()
        if os.path.isfile(file):
            if extension == ".pdf":
                try:
                    pdf_path = file
                    total_pages = count_pages_in_pdf(pdf_path)
                    return total_pages
                except:
                    return 0
            elif extension == ".docx" or extension == ".doc":
                try:
                    docx_path = file
                    total_pages = count_pages_in_docx(docx_path)
                    return total_pages
                except:
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


def count_pages_in_pdf(pdf_path):
    """
    @param pdf_path: Ruta del archivo PDF
    @return: Número de páginas en el documento

    - Cuenta el número de páginas en un archivo PDF utilizando dos métodos diferentes.
    """
    # Primer método: PyPDF2.PdfFileReader
    try:
        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfFileReader(f)
            if not sys.warnoptions:
                warnings.simplefilter("ignore")
            return pdf.getNumPages()
    except Exception as e:
        print(f"Error al contar páginas con PyPDF2.PdfFileReader: {e}")

    # Segundo método: PyPDF2.PdfReader
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error al contar páginas con PyPDF2.PdfReader: {e}")
        return 0


def count_pages_in_docx(doc_path):
    """
    @param doc_path: Ruta del archivo .doc o .docx
    @return: Número de páginas en el documento

    - Cuenta el número de páginas en un archivo .doc o .docx utilizando Microsoft Word.
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
        print(f"Error al contar páginas en el archivo {doc_path}: {e}")
        return 0