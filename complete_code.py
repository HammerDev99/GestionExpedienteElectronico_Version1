# coding=utf-8

import os
import sys
import psutil
import pandas as pd
import shutil
import xlwings as xw
import string
import random
import traceback
from automatizacionData import AutomatizacionData

class AutomatizacionEmpleado:

    ruta = ""
    indice = ""
    files = []
    pids_creados = []

    obj1 = AutomatizacionData()

    def __init__(self, input: str, indice, despacho, subserie, rdo):
        # @param: input tipo str; Obtiene ruta de la carpeta a procesar

        ### Inicializa variables globales con lista de archivos ordenados por nombre
        self.ruta = input

        # LISTAR SOLO LOS ARCHIVOS QUE NO ESTAN OCULTOS (.ds_store)
        self.files = os.listdir(self.ruta)

        if indice == "":
            self.copyXlsm(self.ruta)
        else:
            self.indice = indice

        self.despacho = despacho
        self.subserie = subserie
        self.rdo = rdo

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

    # Renombrar el archivo que quedó como Documento electrónico (por formateo de nombres en indice) también en el sistema de archivos
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

    # Validar sistema de archivos segun SO
    def copyXlsm(self, rutaFinal):
        """
        @param: rutaFinal tipo string; contiene ruta expediente
        @modules: os, shutil
        """

        # Determinar la ruta del archivo xlsm
        if getattr(sys, 'frozen', False):
            # Si se está ejecutando el archivo empaquetado
            bundle_dir = sys._MEIPASS
        else:
            # Si se está ejecutando desde el script original
            bundle_dir = os.path.abspath(os.path.dirname(__file__))

        # La ruta del excel se deja en assets por condiciones actuales
        ruta = os.path.join(bundle_dir, "assets/000IndiceElectronicoC0.xlsm")

        # Copiar el archivo xlsm
        shutil.copy(ruta, rutaFinal)
        self.indice = os.path.join(rutaFinal, "000IndiceElectronicoC0.xlsm")

    # Función pendiente de actualizar
    def createDataFrame(self, files, ruta):
        """
        @return: df (contiene los metadatos)
        @modules: pandas

        - Formatea nombres y los almacena en varias variables
        - Renombra los archivos de la carpeta a procesar
        - Obtiene metadatos de los archivos y carpetas a procesar en un df
        - Adiciona informacion en columna de observaciones para el anexo que conste de un carpeta
        - Renombra archivos de carpetas dentro del expediente
        - Crea df con los datos a registrar en xlsm
        """

        # *********************************************
        # Separar instrucciones en funcion a parte
        nombresExtensiones, nombres, extensiones, numeraciones, ban, nombres_indice = (
            self.obj1.formatNames(ruta, files)
        )

        """ print(nombresExtensiones)
        print(nombres)
        print(extensiones)
        print(numeraciones)
        print(ban)
        print(nombres_indice)
        print(files)
        print(ruta) """

        nombresExtensiones = self.capitalize_first_letter(nombresExtensiones)

        if ban:
            self.renameFiles(files, nombresExtensiones, ruta)
        fullFilePaths = self.fullFilePath(nombresExtensiones, ruta)

        fechamod, tama, cantidadpag, observaciones = self.obj1.getMetadata(
            fullFilePaths
        )
        # *********************************************
        df = pd.DataFrame()
        df["Nombre documento"] = None
        df["Fecha"] = None
        df["Orden"] = None
        df["Paginas"] = None
        df["Formato"] = None
        df["Tamaño"] = None
        df["Origen"] = None
        df["Observaciones"] = None
        for y in range(len(nombres)):
            nueva_fila = pd.Series(
                [
                    str(nombres_indice[y]),
                    str(fechamod[y]),
                    str(numeraciones[y]),
                    str(cantidadpag[y]),
                    str(extensiones[y].replace(".", "")),
                    str(tama[y]),
                    "Electrónico",
                    str(observaciones[y]),
                ],
                index=df.columns,
            )
            df = df.append(nueva_fila, ignore_index=True)
        return df
    
    def capitalize_first_letter(self, file_names):
        capitalized_names = []
        for name in file_names:
            for i, char in enumerate(name):
                if char.isalpha():
                    capitalized_name = name[:i] + char.upper() + name[i+1:]
                    capitalized_names.append(capitalized_name)
                    break
        return capitalized_names

    def fullFilePath(self, files, ruta):
        """
        @param: files tipo list; contiene la lista de archivos
        @param: ruta tipo string; contiene la ruta base
        @modules: os
        @return: pathArchivos tipo List
        """

        pathArchivos = []
        for y in files:
            fulldirct = os.path.join(ruta, y)
            fulldirct.replace("/", "\\")
            pathArchivos.append(fulldirct)
        return pathArchivos

    # Probar usando el modulo OpenPyXl para manipular los archivos de excel
    # https://programacion.net/articulo/como_trabajar_con_archivos_excel_utilizando_python_1419
    # https://openpyxl.readthedocs.io/en/stable/editing_worksheets.html?highlight=insert%20row
    def process(self):
        """
        @param: None
        @modules: xlwings, os, traceback, pandas 
        @return: int
        @modules: xlwings
        """

        #self.close_excel_processes()

        auxFiles, extension = self.separatePath(self.files)  # datos en variales files
        listAux = [os.path.basename(self.indice)]  # datos en carpeta
        indexName, indexExtension = self.separatePath(listAux)

        # extrae el indice de la lista
        for x in range(len(auxFiles)): 
            if auxFiles[x] == indexName[0]:
                auxFiles.pop(x)
                break

        indexPath = self.indice
        app = None # Inicializar app fuera del bloque try

        try:
            wb = xw.Book(indexPath) # Abrir el libro
            app = wb.app # Obtener la aplicación de Excel AQUI SE CREA EL PID

            pid_excel = app.pid # Obtener el PID de la aplicación de Excel
            self.pids_creados.append(pid_excel) # Agregar el PID a la lista de PIDs creados

            app.visible = False  # Hacer que la aplicación de Excel no sea visible
            macro_vba = app.macro(
                "'" + str(os.path.basename(self.indice)) + "'" + "!Macro1InsertarFila"
            )
            sheet = wb.sheets.active # Obtener la hoja activa

            # Crear el DataFrame y realizar el resto de operaciones
            df = self.createDataFrame(self.files, self.ruta)
            self.createXlsm(df, macro_vba, sheet)

            # Guardar y cerrar el libro
            wb.save()
            wb.close()

        except Exception:
            print("Excepcion presentada al intentar acceder al indice electronico\n")
            traceback.print_exc()

        finally:
            if app:  # Si la aplicación de Excel fue creada correctamente
                app.quit()  # Cerrar la aplicación de Excel
                del app  # Eliminar la referencia para liberar memoria

                self.cerrar_procesos_por_pid(self.pids_creados)  # Cerrar los procesos de Excel

        return 1  # Retornar 1 si todo salió bien

    def createXlsm(self, df, macro_vba, sheet):
        """
        @param: df tipo DataFrame; contiene los datos a escribir en el archivo Excel
        @param: macro_vba tipo string; contiene el código VBA para la macro
        @param: sheet tipo string; contiene el nombre de la hoja de Excel
        @modules: pandas, xlwings
        @return: None

        - Agrega nueva columna al df, ejecuta macro tantas veces como filas tenga el df, Ingresa
        registros en el xlsm, Guarda el archivo
        - Obtener la fecha actual para registrar en columna 2 (fecha incorporacion expediente)
        - Agregar columna observaciones
        - Optimizar ejecución de la Macro / Insertar fila con xlwings
        """

        dfcopy = df.iloc[:, 1]
        df.insert(loc=2, column="Fecham", value=dfcopy)
        columnas = ["A", "B", "C", "D", "E", "H", "I", "J", "K"]
        filaInicial = 12
        contFila = filaInicial
        
        for x in range(df.shape[0]):
            macro_vba()

        # Agregar valores de entry01_value y entry02_value en celdas específicas
        try:
            sheet.range("B3").value = self.despacho  # Despacho
            sheet.range("B4").value = self.subserie  # Subserie
            sheet.range("B5").value = self.rdo  # Radicado
        except Exception as e:
            print(f"Error al escribir en las celdas del archivo Excel: {e}")

        for i in range(df.shape[0]):
            for j in range(len(columnas)):
                sheet.range(columnas[j] + str(contFila)).value = df.iloc[i, j]
            contFila = contFila + 1

    def close_excel_processes(self):
        # Iterar sobre todos los procesos en ejecución
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['name'] == 'EXCEL.EXE':
                try:
                    # Finalizar el proceso de Excel
                    os.kill(proc.info['pid'], 9)  # 9 es la señal para "matar" el proceso
                    print(f"Finalizado proceso de Excel con PID: {proc.info['pid']}")
                except Exception as e:
                    print(f"No se pudo finalizar el proceso de Excel con PID: {proc.info['pid']}. Error: {e}")

    def cerrar_procesos_por_pid(self, pids):
        """
        Cierra los procesos especificados en la lista de PID.
        @param: pids tipo list; lista de PID de los procesos a cerrar
        """
        for pid in pids:
            try:
                proc = psutil.Process(pid)
                proc.kill()  # forzar el cierre
                print(f"Proceso {proc.name()} con PID {pid} cerrado.")
                self.pids_creados.remove(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                print(f"No se pudo cerrar el proceso con PID {pid}: {e}")

import datetime
import re
import os
import string
import sys
import warnings
import PyPDF2
import random 
import win32com.client as win32


class AutomatizacionData:

    def __init__(self):
        pass


    def getMetadata(self, files):
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
        Establece la carpeta de comentarios contando las ocurrencias de cada extensión.
        Args:
            extensiones (List): Una lista de extensiones de archivos.
        Returns:
            Dict: Un diccionario con las extensiones como claves y sus conteos como valores.
        Ejemplo:
            >>> set_comments_folder(['.txt', '.pdf', '.txt'])
            {'.txt': 2, '.pdf': 1}
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
        Separa los nombres de archivo y sus extensiones de una lista de rutas de archivos.
        Args:
            files (List[str]): Una lista de rutas de archivos.
        Returns:
            Tuple[List[str], List[str]]: Dos listas, una que contiene los nombres de archivo sin extensiones,
                                         y la otra que contiene las extensiones de archivo.
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
    def renameFiles(self, files, nombresExtensiones, ruta):
        """
        Renombra una lista de archivos a nuevos nombres proporcionados en `nombresExtensiones`. Si un archivo no existe,
        agrega una cadena aleatoria al nuevo nombre.
        Args:
            files (list): Lista de nombres de archivos a renombrar.
            nombresExtensiones (list): Lista de nuevos nombres de archivos con extensiones.
            ruta (str): Ruta del directorio donde se encuentran los archivos.
        Modules:
            os
        Raises:
            Exception: Si ocurre un error durante el renombrado, se captura una excepción y se imprime un mensaje.
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
        Formatea los nombres de archivos y directorios en una ruta dada.
        Args:
            ruta (str): La ruta al directorio que contiene los archivos.
            files (list): Una lista de nombres de archivos y directorios a procesar.
        Returns:
            tuple: Una tupla que contiene los siguientes elementos:
                - nombresExtensiones (list): Lista de nombres formateados con extensiones.
                - nombres (list): Lista de nombres formateados sin extensiones.
                - extensiones (list): Lista de extensiones de archivos o 'Carpeta' para directorios.
                - numeraciones (list): Lista de números consecutivos para cada archivo.
                - ban (bool): Indicador que señala si los archivos no están en orden.
                - nombres_indice (list): Lista de nombres procesados del índice.
        Modules:
            re, os, string
        Functionality:
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
                resultado = "Documento electronico"

            if len(resultado) > 36:
                resultado = resultado[:36]

            lista_cadena[i] = resultado  # Modificar la cadena de la lista
        return lista_cadena

    def isOrderCorrect(self, files, nombresExtensiones):
        """
        Verifica el orden de los archivos consecutivos.
        Args:
            files (List): Lista de nombres de archivos.
            nombresExtensiones (List): Lista de nombres de archivos esperados con extensiones.
        Returns:
            bool: True si el orden es incorrecto, False en caso contrario.
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
        print(f"Error al contar páginas en el archivo {doc_path}: {e}")
        return 0
    
# coding=utf-8

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
import sys
import webbrowser
import requests
import json
from automatizacionEmpleado import AutomatizacionEmpleado
from carpetas_analyzer import CarpetasAnalyzer
from tooltip import Tooltip

import csv

class Application(ttk.Frame):

    expediente = ""
    carpetas = []
    is_updated = True
    selected_value = "2"
    lista_subcarpetas = []
    analyzer = None

    def __init__(self, root, is_updated=True):
        """
        @param: root tipo Tk; contiene la raíz de la aplicación Tkinter
        @modules: tkinter
        - Inicializa la aplicación, configura la ventana principal y crea los widgets.
        """

        super().__init__(root)
        root.title("GestionExpedienteElectronico")
        root.resizable(False, False)
        # root.geometry("350x300")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pack(padx=20, pady=20)  # Añadir padding aquí
        self.create_oneProcessWidgets()

    def create_oneProcessWidgets(self):
        """
        @modules: tkinter
        - Crea y configura los widgets de la interfaz gráfica.
        """
        self.is_updated = self.comprobar_actualizaciones() # Comprobar actualizaciones al iniciar la aplicación

        self.label = tk.Label(self, text=r"Daniel Arbelaez Alvarez - HammerDev99", fg="blue", cursor="hand2")
        self.label.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label.bind(
            "<Button-1>",
            lambda e: self.callback(
                "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1"
            ),
        )

        if not self.is_updated:
            # Crear un contenedor para el label de actualización
            self.update_frame = tk.Frame(self)
            self.update_frame.pack(side=tk.TOP, fill=tk.X)

            self.update_label = tk.Label(
                self.update_frame, text="🚀 Nueva versión disponible", fg="green", cursor="hand2"
            )
            self.update_label.pack(side=tk.RIGHT, padx=0, pady=0)
            self.update_label.bind(
                "<Button-1>",
                lambda e: self.callback(
                    "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/latest"
                ),
            )

        self.label01 = tk.Label(
            self, text="Juzgado", 
            font=("Helvetica", 12)
        )
        self.label01.pack(pady=5)

        self.entry01 = tk.Entry(self, width=90, justify="center")
        self.entry01.pack(pady=5)
        self.entry01.insert(0, "CENTRO DE SERVICIOS JUDICIALES DE BELLO")

        self.label02 = tk.Label(
            self, text="Serie o Subserie", 
            font=("Helvetica", 12)
        )
        self.label02.pack(pady=5)

        # Crear el Combobox para entry02
        self.entry02 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry02.pack(pady=5)

        # Leer el archivo CSV y obtener los valores para el Combobox
        self.load_csv_values()

        # El radicado se obtendrá mediante la selección del usuario sobre la estructura de carpetas que tenga
        """ # Label y entry para la variable rdo
        self.label03 = tk.Label(
            self, text="Radicado", 
            font=("Helvetica", 12)
        )
        self.label03.pack(pady=5)

        self.entry03 = tk.Entry(self, width=50)
        self.entry03.pack(pady=5)
        self.entry03.insert(0, "")

        self.label1 = tk.Label(
            self, text="(Dejar en blanco si el nombre de las subcarpetas corresponde al número de radicado)", 
            font=("Helvetica", 11)
        )
        self.label1.pack(pady=1) """

        # Crear un Frame para los Radiobuttons
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=5)

        # Variable para los Radiobuttons
        self.radio_var = tk.StringVar(value="2")
        self.radio_var.trace("w", self.on_radio_change)

        # Crear los Radiobuttons
        """ self.radio1 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de una \nsola carpeta específica", variable=self.radio_var, value="1")
        self.radio1.pack(side=tk.LEFT, padx=10) """
        self.radio2 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de todas \nlas carpetas internas de un \nexpediente", variable=self.radio_var, value="2")
        self.radio2.pack(side=tk.LEFT, padx=10)
        self.radio3 = ttk.Radiobutton(self.radio_frame, text="Opción 2: Índice de múltiples \nexpedientes de una serie o \nsubserie documental", variable=self.radio_var, value="3")
        self.radio3.pack(side=tk.LEFT, padx=10)

        # Crear tooltips con imágenes para los Radiobuttons
        self.create_tooltips()

        """ self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(fill="x", padx=5) """
        # self.scrollbar.config(command=self.entry1.xview)
        # Crear una barra de desplazamiento vertical
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        """ self.entry1 = tk.Entry(self, width=50, xscrollcommand=self.scrollbar.set)
        self.entry1.config(state=tk.DISABLED)
        self.entry1.insert("end", str(dir(tk.Scrollbar)))
        self.entry1.pack(fill="x", before=self.scrollbar) """
        # Crear un Text widget para mostrar los RDOs procesados
        self.text_widget = tk.Text(self, width=50, height=20, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        self.text_widget.insert(tk.END, "Instrucciones de Uso del Programa\n\n1. Descargar la(s) carpeta(s): NO DEBEN TENER ÍNDICE.\n\n2. Validar esquema de carpetas: Asegúrate de que la estructura interna de carpetas cumple con el protocolo. Ejemplo:\n\n  -Opción 1: 05088/01PrimeraInstancia/C01Principal/Archivos\n  -Opción 2: 2024/05088/01PrimeraInstancia/C01Principal/Archivos\n\n3. El radicado debe tener 23 dígitos y los nombres de los archivos deben tener un orden mínimo.\n\n4. Datos del SGDE: Ingresar exactamente los mismos datos de 'Juzgado' y 'serie o subserie' que registra en el SGDE.\n\n")

        # Configurar la barra de desplazamiento para el Text widget
        self.scrollbar.config(command=self.text_widget.yview)

        self.pathExpediente = tk.Button(
            self,
            text="Agregar carpeta",
            command=self.obtener_rutas,
            height=1,
            width=17,
        )
        self.pathExpediente.pack(side=tk.LEFT, padx=5)

        # Barra de progreso
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=5)

        # Botón Aceptar
        self.aceptar = tk.Button(
            self, text="Aceptar", command=self.procesa_expedientes, height=1, width=7
        )
        self.aceptar.pack(side=tk.LEFT, padx=5)

        # Botón Cancelar
        self.cancelar = tk.Button(
            self, text="Cancelar", fg="red", command=self.on_closing, height=1, width=7
        )
        self.cancelar.pack(side=tk.LEFT, padx=5)

        # Otros widgets...
        self.label5 = tk.Label(self, text="")
        self.label5.pack(side=tk.LEFT)

        self.pack()

    def on_radio_change(self, *args):
        self.selected_value = self.radio_var.get()
        #print(f"El valor del Radiobutton ha cambiado a: {selected_value}")

    def get_radio_value(self):
        selected_value = self.radio_var.get()
        print(f"Valor seleccionado: {selected_value}")

    def create_tooltips(self):
        """
        Crea tooltips para los radiobuttons usando imágenes.
        """
        image_paths = [
            self.get_bundled_path('assets/tooltip1.png'),
            self.get_bundled_path('assets/tooltip2.png'),
            self.get_bundled_path('assets/tooltip3.png')
        ]

        # Tooltip(self.radio1, image_paths[0])  # Comentado
        Tooltip(self.radio2, image_paths[1])
        Tooltip(self.radio3, image_paths[2])

    def callback(self, url):
        """
        @modules: webbrowser
        """
        webbrowser.open_new(url)

    def on_closing(self):
        """
        @modules: tkinter
        - Maneja el evento de cierre de la ventana principal.
        """
        print("Cerrando aplicación")
        root.destroy()
        # root.quit()

    def load_csv_values(self):
        """
        Carga los valores del archivo CSV en el combobox.
        """
        csv_file_path = self.get_bundled_path('assets/TRD.csv')
        values = []
        
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                values.append(row['nombre'].upper())
                
        self.entry02['values'] = values
        if values:
            self.entry02.set(values[0])

    # Funcion para el caso de varias carpetas (4 y 5 niveles: carpeta/subcarpetas/archivos)
    def obtener_rutas(self):
        """
        - Obtiene la ruta seleccionada por el usuario
        - Recupera la lista de carpetas en esa ruta
        - Valida la estructura de las carpetas
        - Obtiene los CUIs y subcarpetas internas
        """
        self.lista_cui = []
        self.lista_subcarpetas = []
        self.carpetas_omitidas = set()
        self.estructura_directorios = {}

        folder_selected = os.path.normpath(filedialog.askdirectory())
        if folder_selected in [".", ""]:
            tk.messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carpeta.")
            return

        self.expediente = folder_selected

        analyzer = CarpetasAnalyzer({}, None)
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            tk.messagebox.showwarning("Advertencia", "La carpeta seleccionada está vacía o no es accesible.")
            return

        #print("Estructura de Directorios:", estructura_directorios)
        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        analyzer = CarpetasAnalyzer(estructura_directorios, profundidad_maxima)

        if self.selected_value == "2" and profundidad_maxima == 4:
            self.profundidad = 4
            lista_cui, lista_subcarpetas = analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 4, folder_selected)
            self.handle_directory_analysis(folder_selected, estructura_directorios, lista_cui, lista_subcarpetas, self.carpetas_omitidas, None)
            self.lista_subcarpetas = lista_subcarpetas
            self.analyzer = analyzer
        elif self.selected_value == "3" and profundidad_maxima == 5:
            self.profundidad = 5
            lista_cui, lista_subcarpetas = analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 5, None)
            self.handle_directory_analysis(folder_selected, estructura_directorios, lista_cui, 
            lista_subcarpetas, self.carpetas_omitidas, analyzer)
            self.lista_subcarpetas = lista_subcarpetas
            self.analyzer = analyzer
        else:
            tk.messagebox.showwarning(
                "Advertencia", 
                "La estructura de directorios no coincide con la OPCIÓN seleccionada.\n\n"
                "Por favor, verifique la estructura interna de los directorios seleccionados."
            )

        # Imprimir las listas para verificación
        """ print("Estructura de Directorios:", self.estructura_directorios)
        print("Lista de C.U.I.:", self.lista_cui)
        print("Lista de Subcarpetas Internas:", self.lista_subcarpetas)
        print("Carpetas Omitidas:", self.carpetas_omitidas) """

    def _validar_cui(self, cui):
        """
        Valida que el CUI tenga exactamente 23 dígitos sin caracteres especiales.
        
        Args:
            cui (str): String a validar
            
        Returns:
            tuple: (bool, str) - (Es válido, CUI limpio)
        """
        # Eliminar espacios y cualquier texto después de estos
        cui = cui.split()[0]
        #print(f"CUI: {cui}")
        # Remover caracteres especiales y no numéricos
        cui_limpio = ''.join(c for c in cui if c.isdigit())
        #print(f"CUI limpio: {cui_limpio}")
        # Verificar que tenga exactamente 23 dígitos
        return (len(cui_limpio) >= 23, cui_limpio[:23] if len(cui_limpio) >= 23 else cui)

    def handle_directory_analysis(self, folder_selected, estructura_directorios, lista_cui, lista_subcarpetas, carpetas_omitidas = None, analyzer = None):
        """
        @param: folder_selected tipo str, estructura_directorios tipo dict, lista_cui tipo list, lista_subcarpetas tipo list, carpetas_omitidas tipo set

        Muestra mensaje de carpeta seleccionada
        Guarda las listas en atributos de la clase
        Muestra mensaje de carpetas omitidas
        """
        self.text_widget.insert(tk.END, f"\n*******************\nCarpeta seleccionada: {folder_selected}")
        self.text_widget.see(tk.END)

        # Conjuntos para almacenar CUIs válidos e inválidos
        cuis_validos = set()
        cuis_invalidos = set()

        # Procesar cada sublista en lista_subcarpetas
        if self.selected_value == "3":
            for sublista in lista_subcarpetas:
                for ruta in sublista:
                    # Obtener la parte antes del primer backslash
                    cui = ruta.split('\\')[0]
                    
                    # Validar el CUI
                    es_valido, cui_procesado = self._validar_cui(cui)
                    if es_valido:
                        cuis_validos.add(cui_procesado)
                    else:
                        cuis_invalidos.add(cui)
        else:
            for cui in lista_cui:
                es_valido, cui_procesado = self._validar_cui(cui)
                if es_valido:
                    cuis_validos.add(cui_procesado)
                else:
                    cuis_invalidos.add(cui)

        # Actualiza las listas en atributos de la clase
        try:
            self.lista_cui = lista_cui
            self.lista_subcarpetas = lista_subcarpetas
            self.estructura_directorios = estructura_directorios
            if self.selected_value == "3":
                self.carpetas_omitidas = analyzer.encontrar_cuis_faltantes(lista_cui, lista_subcarpetas)
        except Exception as e:
            print(f"Error al guardar las listas en atributos de la clase: {str(e)}")
        
        # Mostrar carpetas omitidas
        try:
            if self.carpetas_omitidas:
                mensaje = f"Se encontraron {len(self.carpetas_omitidas)} carpetas que no cumplen con la estructura de directorios"
                self.mensaje(None, mensaje)
                mensaje = "Las siguientes carpetas no cumplen con la estructura de carpetas y no serán incluidas en el procesamiento:\n"
                for carpeta in sorted(self.carpetas_omitidas):
                    mensaje += f"- {carpeta}\n"
                self.text_widget.insert(tk.END, mensaje + "\n")
                self.text_widget.see(tk.END)
        except Exception as e:
            print(f"Error al mostrar las carpetas omitidas: {str(e)}. No se eligio una estructura de carpetas adecuada")

        # Muestra los CUIs inválidos
        if cuis_invalidos:
            mensaje = "Se encontraron carpetas que no cumplen con el formato de 23 dígitos:\n"
            if self.selected_value == "3":
                for cui in sorted(cuis_invalidos):
                    mensaje += f"- {cui}\n"
            else:
                for cui in lista_cui:
                    mensaje += f"- {cui}\n"
            self.text_widget.insert(tk.END, mensaje)
            self.text_widget.see(tk.END)
            self.mensaje(None, "Algunas carpetas no cumplen con el formato requerido de 23 dígitos numéricos.")

    def procesa_expedientes(self):
        """
        - Obtiene Lista de Subcarpetas Internas para procesar
        - Valida radicados unicamente obteniendo los primeros 23 digitos
        - Confirma procedimiento con el usuario
        - Crea objeto y llama metodo procesaCarpetas() u otro en su defecto para cada expediente en la lista
        - Genera reporte de lista de rutas procesadas
        """
        lista_subcarpetas = self.lista_subcarpetas
        analyzer = self.analyzer

        total_carpetas = sum(len(sublista) for sublista in lista_subcarpetas)
        self.progress["maximum"] = 1  # La barra de progreso va de 0 a 1

        if lista_subcarpetas != []:	
            num_carpetas = total_carpetas
            if tk.messagebox.askyesno(
                    message=f'Se procesarán {num_carpetas} carpetas que contiene la carpeta "{os.path.basename(self.expediente)}". \n¿Desea continuar?.',
                    title=os.path.basename(self.expediente),
                ):
                # Indicar al usuario que el proceso ha comenzado
                self.progress["value"] = 0.1
                self.text_widget.insert(tk.END, "\nProceso iniciado...\n")
                # self.text_widget.insert(tk.END, "CARPETAS PROCESADAS:\n")
                self.update_idletasks()

                i = 0
                for sublista in lista_subcarpetas:
                    despacho = self.entry01.get()
                    subserie = self.entry02.get()
                    for ruta in sublista:

                        # Obtiene el valor del radicado
                        if self.selected_value == "2":
                            rdo = os.path.normpath(os.path.basename(self.expediente))
                            rdo = analyzer._formater_cui(rdo)
                        elif self.selected_value == "3":
                            rdo = os.path.normpath(ruta)
                            rdo = analyzer._formater_cui(rdo)

                        # Muestra en el widget de texto la ruta subserie/radicado
                        self.text_widget.insert(tk.END, "- "+os.path.normpath(os.path.basename(self.expediente)+"/"+ruta)+"\n")
                        # Asegura que el último texto insertado sea visible
                        self.text_widget.see(tk.END)

                        # Concatena la ruta con la carpeta a procesar y normaliza la ruta
                        carpeta = self.get_bundled_path(os.path.normpath(os.path.join(self.expediente, ruta)))
                        print("Carpeta a procesar:", carpeta)
                        # Crea una instancia de AutomatizacionEmpleado con los parámetros necesarios
                        obj = AutomatizacionEmpleado(carpeta, "", despacho, subserie, rdo)
                        obj.process()

                        # Actualiza la barra de progreso basado en el progreso actual (10% inicial + progreso proporcional)
                        self.progress["value"] = 0.1 + ((i + 1) / num_carpetas) * 0.9
                        # Actualiza la interfaz gráfica para mostrar el progreso
                        self.update_idletasks()
                    i = i + 1
                # Indicar al usuario que el proceso ha terminado
                self.progress["value"] = 1.0  # Asegurarse de que la barra de progreso llegue al 100%
                self.update_idletasks()
                self.expediente = ""
                self.carpetas = []
                self.lista_cui = []
                self.lista_subcarpetas = []
                self.estructura_directorios = {}
                self.analyzer = None
                self.text_widget.insert(tk.END, "Proceso completado.\n*******************\n")
                self.progress["value"] = 0
                self.update_idletasks()
                self.mensaje(1)
            else:
                self.expediente = ""
                self.carpetas = []
                self.mensaje(6)
        else:
            self.mensaje(3)

    def mensaje(self, result = None, mensaje = None):
        """
        @param: result tipo int
        @modules: tkinter
        - Utiliza la GUI para enviar mensaje
        """
        switcher = {
            0: "Procedimiento detenido. No se encontraron los archivos indicados en el índice",
            1: "Procedimiento finalizado",
            2: "Archivos sin procesar",
            3: "Seleccione una carpeta para procesar",
            4: "Agregue archivos a la lista",
            5: "La carpeta electrónica del expediente se encuentra actualizada",
            6: "Procedimiento detenido"
        }
        if result != None:
            tk.messagebox.showinfo(
                message=switcher.get(result), title=os.path.basename(self.expediente)
            )
            self.text_widget.insert(tk.END, "\n")
            # self.text_widget.insert(tk.END, switcher.get(result))
            lista_vacia = list()
            self.agregaNombreBase(lista_vacia, False)
        
        if mensaje != None:
            tk.messagebox.showinfo(
                message=mensaje, title=os.path.basename(self.expediente)
            )

    def agregaNombreBase(self, items, bandera):
        """
        @param: items tipo List, bandera tipo bool;  items contiene nombre(s) de archivo(s)
        @widgets: listbox1, entry1
        - Crea lista auxiliar con nombres base de items
        - Bandera controla Widget a modificar
        """

        nombres = []
        if bandera:
            for x in items:
                nombres.append(os.path.basename(x))
            self.listbox1.delete(0, tk.END)
            self.listbox1.insert(0, *nombres)
        else:
            """ self.entry1.config(state=tk.NORMAL)
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, items)
            self.entry1.config(state=tk.DISABLED) """

    def get_bundled_path(self, ruta):
        """
        Obtiene la ruta correcta según el entorno de ejecución.
        
        Args:
            ruta (str): Ruta relativa al directorio base
            
        Returns:
            str: Ruta absoluta normalizada
        """
        bundle_dir = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.dirname(__file__))
        return os.path.normpath(os.path.join(bundle_dir, ruta))

    def obtener_version_actual(self):
        # Determinar la ruta del archivo xlsm
        ruta_json = self.get_bundled_path('assets/last_version.json')
        with open(ruta_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            version = data.get('version')
        return version

    def comprobar_actualizaciones(self):
        url = "https://raw.githubusercontent.com/HammerDev99/GestionExpedienteElectronico_Version1/refs/heads/master/assets/last_version.json"  # O usa la URL de raw.githubusercontent.com
        try:
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            version_actual = list(map(int, self.obtener_version_actual().split(".")))
            ultima_version = list(map(int, datos.get('version').split(".")))

            if version_actual < ultima_version:
                # Actualizar variable para mostrar notificación en un label de la GUI
                return False # la variable is_updated se actualiza a False
            else:
                return True # la variable is_updated se mantiene en True
        except requests.RequestException as e:
            print(f"Error al comprobar actualizaciones: {e}")

root = tk.Tk()
app = Application(root)
app.mainloop()

import os

class CarpetasAnalyzer:
    def __init__(self, estructura_directorios, profundidad_maxima = None):
        self.estructura_directorios = estructura_directorios
        self.profundidad_maxima = profundidad_maxima
        self.todas_las_carpetas = set()
        self.carpetas_procesadas = set()
        self.problemas = []

    # getters y setters para los atributos
    def get_estructura_directorios(self):
        return self.estructura_directorios
    
    def set_estructura_directorios(self, estructura_directorios):
        self.estructura_directorios = estructura_directorios

    def get_profundidad_maxima(self):
        return self.profundidad_maxima
    
    def set_profundidad_maxima(self, profundidad_maxima):
        self.profundidad_maxima = profundidad_maxima

    def get_todas_las_carpetas(self):
        return self.todas_las_carpetas
    
    def set_todas_las_carpetas(self, todas_las_carpetas):
        self.todas_las_carpetas = todas_las_carpetas

    def get_carpetas_procesadas(self):
        return self.carpetas_procesadas
    
    def set_carpetas_procesadas(self, carpetas_procesadas):
        self.carpetas_procesadas = carpetas_procesadas

    def get_problemas(self):
        return self.problemas
    
    def set_problemas(self, problemas):
        self.problemas = problemas

    def obtener_todas_carpetas(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """Obtiene todas las carpetas en un nivel específico."""
        todas_carpetas = set()
        
        if self._es_nivel_objetivo(nivel_actual, nivel_deseado, directorio):
            ruta_normalizada = os.path.normpath(ruta_actual.lstrip('/'))
            todas_carpetas.add(ruta_normalizada)
            return todas_carpetas
        
        if not isinstance(directorio, dict) or not directorio:
            return todas_carpetas
        
        for nombre, subdirectorio in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
            todas_carpetas.update(self.obtener_todas_carpetas(
                subdirectorio,
                nivel_deseado,
                nivel_actual + 1,
                nueva_ruta
            ))
        return todas_carpetas

    def _es_nivel_objetivo(self, nivel_actual, nivel_deseado, directorio):
        """Verifica si el nivel actual es el objetivo y es un directorio válido."""
        return nivel_actual == nivel_deseado and isinstance(directorio, dict) and directorio

    def _validar_instancia(self, directorio, ruta):
        """Valida la estructura de instancia judicial."""
        if not any(key.lower().startswith(("primera", "segunda")) for key in directorio.keys()):
            self.problemas.append(f"Ruta '{ruta}' no contiene carpeta de instancia válida")

    def _validar_anio(self, ruta):
        """Valida que el nombre de la carpeta contenga mínimo 23 digitos al inicio sin espacios"""
        try:
            anio = int(os.path.basename(ruta))
            if not (1900 <= anio <= 2100):  # Rango razonable de años
                raise ValueError
        except ValueError:
            self.problemas.append(f"Ruta '{ruta}' no corresponde a un año válido")

    def _analizar_estructura_nivel(self, directorio, nivel, ruta):
        """Analiza la estructura en un nivel específico."""
        if not isinstance(directorio, dict):
            self.problemas.append(f"Ruta '{ruta}' no es un directorio válido")
            return

        if self.profundidad_maxima == 4 and nivel == 2:
            self._validar_instancia(directorio, ruta)
        elif self.profundidad_maxima == 5 and nivel == 1:
            self._validar_anio(ruta)

    def analizar_estructura(self, directorio=None, nivel=0, ruta=""):
        """Analiza recursivamente la estructura del directorio."""
        if directorio is None:
            directorio = self.estructura_directorios

        self._analizar_estructura_nivel(directorio, nivel, ruta)
        
        if isinstance(directorio, dict):
            for nombre, subdirectorio in directorio.items():
                nueva_ruta = os.path.join(ruta, nombre) if ruta else nombre
                self.analizar_estructura(subdirectorio, nivel + 1, nueva_ruta)

    def procesar_carpetas(self):
        """Identifica las carpetas que cumplen con la estructura esperada."""
        for nombre, subdirectorio in self.estructura_directorios.items():
            if not isinstance(subdirectorio, dict):
                continue
                
            if self.profundidad_maxima == 4:
                self.carpetas_procesadas.add(nombre)
            elif self.profundidad_maxima == 5:
                for subnombre, subsubdirectorio in subdirectorio.items():
                    if isinstance(subsubdirectorio, dict):
                        self.carpetas_procesadas.add(os.path.join(nombre, subnombre))

    def generar_reporte(self):
        """Genera el reporte final del análisis."""
        self.todas_las_carpetas = self.obtener_todas_carpetas(self.estructura_directorios, 2)
        self.procesar_carpetas()
        self.analizar_estructura()
        
        carpetas_omitidas = self.todas_las_carpetas - self.carpetas_procesadas
        
        return {
            "total_carpetas": len(self.todas_las_carpetas),
            "carpetas_procesadas": len(self.carpetas_procesadas),
            "carpetas_omitidas": len(carpetas_omitidas),
            "lista_omitidas": sorted(list(carpetas_omitidas)),
            "problemas_detectados": self.problemas
        }
    
    def obtener_rutas_nivel(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """
        Obtiene las rutas de un nivel específico normalizando los separadores.
        """
        rutas = []
        if nivel_actual == nivel_deseado:
            if ruta_actual:  # Solo normalizar si hay una ruta
                ruta_actual = os.path.normpath(ruta_actual)
            rutas.append(ruta_actual)
        elif isinstance(directorio, dict):
            for nombre, subdirectorio in directorio.items():
                nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
                rutas.extend(self.obtener_rutas_nivel(subdirectorio, nivel_deseado, nivel_actual + 1, nueva_ruta))
        return rutas

    def obtener_todas_carpetas(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """
        Obtiene todas las carpetas existentes en un nivel específico.
        
        Args:
            directorio (dict): Estructura de directorios
            nivel_deseado (int): Nivel de profundidad objetivo
            nivel_actual (int): Nivel actual en la recursión
            ruta_actual (str): Ruta acumulada
        
        Returns:
            set: Conjunto de todas las carpetas en el nivel especificado
        """
        todas_carpetas = set()
        
        if nivel_actual == nivel_deseado:
            if isinstance(directorio, dict) and directorio:
                ruta_normalizada = os.path.normpath(ruta_actual.lstrip('/'))
                todas_carpetas.add(ruta_normalizada)
            return todas_carpetas
            
        if not isinstance(directorio, dict) or not directorio:
            return todas_carpetas
            
        for nombre, subdirectorio in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
            todas_carpetas.update(self.obtener_todas_carpetas(
                subdirectorio,
                nivel_deseado,
                nivel_actual + 1,
                nueva_ruta
            ))
        
        return todas_carpetas

    def _validar_profundidad(self, profundidad):
        """Valida que la profundidad sea 4 o 5."""
        if profundidad not in [4, 5]:
            raise ValueError("La profundidad máxima debe ser 4 o 5")

    def _normalizar_rutas(self, rutas):
        """Normaliza una lista de rutas."""
        return [os.path.normpath(ruta) for ruta in rutas]

    def _procesar_nivel_dos(self, dir_actual, ruta_base):
        """Procesa las carpetas de nivel 2."""
        ruta_base = os.path.normpath(ruta_base) if ruta_base else ""
        todas_nivel_dos = {
            os.path.normpath(ruta) 
            for ruta in self.obtener_todas_carpetas(dir_actual, 2, 1, ruta_base)
        }
        rutas_nivel_dos = self.obtener_rutas_nivel(dir_actual, 2, 1, ruta_base)
        rutas_nivel_cuatro = self.obtener_rutas_nivel(dir_actual, 4, 1, ruta_base)
        
        return todas_nivel_dos, rutas_nivel_dos, rutas_nivel_cuatro

    def _procesar_directorio_profundidad_4(self, directorio):
        """Procesa directorios con profundidad 4."""
        return [
            (subdirectorio, nombre)
            for nombre, subdirectorio in directorio.items()
        ]

    def _procesar_directorio_profundidad_5(self, directorio):
        """Procesa directorios con profundidad 5."""
        return [
            (subsubdirectorio, os.path.join(nombre, subnombre))
            for nombre, subdirectorio in directorio.items()
            for subnombre, subsubdirectorio in subdirectorio.items()
        ]

    def obtener_lista_rutas_subcarpetas(self, directorio, profundidad_maxima, folder_selected=None):
        """
        Obtiene las listas de CUIs, subcarpetas y carpetas omitidas según la profundidad.
        
        Args:
            directorio (dict): Estructura de directorios
            profundidad_maxima (int): Profundidad máxima (4 o 5)
        
        Returns:
            tuple: (lista_cui, lista_rutas_subcarpetas, carpetas_omitidas)
        """
        try:
            self._validar_profundidad(profundidad_maxima)
            
            lista_rutas_subcarpetas = []
            lista_cui = []
            todas_las_carpetas = set()
            carpetas_procesadas = set()

            # Seleccionar procesamiento según profundidad
            directorios_a_procesar = (
                self._procesar_directorio_profundidad_4(directorio) 
                if profundidad_maxima == 4 
                else self._procesar_directorio_profundidad_5(directorio)
            )

            # Procesar cada directorio
            for dir_actual, ruta_base in directorios_a_procesar:
                todas_nivel_dos, rutas_nivel_dos, rutas_nivel_cuatro = self._procesar_nivel_dos(
                    dir_actual, ruta_base
                )
                
                todas_las_carpetas.update(todas_nivel_dos)
                
                if rutas_nivel_dos:
                    rutas_normalizadas = self._normalizar_rutas(rutas_nivel_dos)
                    lista_rutas_subcarpetas.append(rutas_normalizadas)
                    carpetas_procesadas.update(rutas_normalizadas)
                
                """ if rutas_nivel_cuatro:
                    lista_cui.extend(self._normalizar_rutas(rutas_nivel_cuatro)) """
                
                # Validar con opcion 1 con opcion 2 ya es funcional
                if folder_selected:
                    if os.path.basename(folder_selected) not in lista_cui:
                        lista_cui.append(os.path.basename(folder_selected))
                else:
                    cui = self._extraer_cui(ruta_base)
                    if cui and cui not in lista_cui:  # Solo añadir CUIs únicos
                        lista_cui.append(cui)

            return lista_cui, lista_rutas_subcarpetas

        except Exception as e:
            print(f"Error al procesar la estructura de directorios: {str(e)}")
            return [], [], set()

    
    def encontrar_cuis_faltantes(self, lista_cui, lista_subcarpetas_internas):
        """
        Encuentra los CUIs que no tienen carpetas internas correspondientes.
        
        Args:
            lista_cui: Lista de CUIs
            lista_subcarpetas_internas: Lista de listas con rutas de carpetas
        
        Returns:
            list: CUIs que no tienen carpetas internas
        """
        # Extraer todos los CUIs de las subcarpetas (antes del primer \\)
        cuis_en_subcarpetas = set()
        for sublista in lista_subcarpetas_internas:
            for ruta in sublista:
                cui = ruta.split('\\')[0]
                cuis_en_subcarpetas.add(cui)
        
        # Encontrar CUIs que no están en las subcarpetas
        cuis_faltantes = [cui for cui in lista_cui if cui not in cuis_en_subcarpetas]
        
        return cuis_faltantes

    def _extraer_cui(self, ruta):
        """Extrae el CUI (radicado) de una ruta."""
        partes = ruta.split('\\')
        return partes[0] if partes else None
    
    def _formater_cui(self, ruta):
        """
        Extrae el CUI (radicado) de una ruta y limpia caracteres no deseados.
        
        Args:
            ruta (str): Ruta completa del archivo
            
        Returns:
            str: CUI limpio (solo dígitos) o None si no hay datos válidos
        """
        try:
            # Obtener la primera parte de la ruta (antes del primer backslash)
            partes = ruta.split('\\')
            if not partes:
                return None

            # Tomar solo la primera parte y eliminar espacios iniciales y finales
            cui = partes[0].strip()

            # Extraer solo los dígitos
            cui_limpio = ''.join(caracter for caracter in cui if caracter.isdigit())

            # Verificar que tengamos al menos un dígito
            return cui_limpio if cui_limpio else None

        except Exception as e:
            print(f"Error al extraer CUI: {str(e)}")
            return None

    # Función recursiva para construir el diccionario de estructura de directorios
    def construir_estructura(self, ruta):
        estructura = {}
        for item in os.listdir(ruta):
            item_path = os.path.join(ruta, item)
            if os.path.isdir(item_path):
                estructura[item] = self.construir_estructura(item_path)
            else:
                estructura[item] = None
        return estructura
    
    def obtener_profundidad_maxima(self, directorio, nivel_actual=1):
        if not isinstance(directorio, dict) or not directorio:
            # Si no es un diccionario o está vacío, la profundidad es el nivel actual
            return nivel_actual
        else:
            # Calcula la profundidad recursivamente en cada subdirectorio
            return max(self.obtener_profundidad_maxima(subdirectorio, nivel_actual + 1) for subdirectorio in directorio.values())
        
# coding=utf-8

import automatizacionGUI
import sys

def main():
    # Punto de entrada
    try:
        obj = automatizacionGUI()
        obj.__init__()
    except Exception as e:
        #print(e)
        sys.exit(0)

if __name__ == '__main__':
    main()

import tkinter as tk
from PIL import Image, ImageTk

class Tooltip:
    def __init__(self, widget, image_path, y_offset=25):
        self.widget = widget
        self.image_path = image_path
        self.y_offset = y_offset
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.image_path:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25 + self.y_offset

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        image = Image.open(self.image_path)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(tw, image=photo)
        label.image = photo  # Mantener una referencia para evitar que la imagen sea recolectada por el garbage collector
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None