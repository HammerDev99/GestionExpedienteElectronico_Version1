# coding=utf-8

import os
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

    obj1 = AutomatizacionData()

    """ def __init__(self) -> None: # Only for test
        pass """

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

        # Obtener la ruta actual del archivo
        current_dir = os.getcwd()

        # Unir dos partes de una ruta de archivo
        ruta = os.path.join(current_dir, "src/app/assets", "000IndiceElectronicoC0.xlsm")
        # print(ruta + "\n" + rutaFinal)
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

    def fullFilePath(self, files, ruta):
        """
        @param: files (List); ruta (string)
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
        @return: int
        @modules: xlwings
        """

        auxFiles, extension = self.separatePath(self.files)  # datos en variales files
        listAux = [os.path.basename(self.indice)]  # datos en carpeta
        indexName, indexExtension = self.separatePath(listAux)
        for x in range(len(auxFiles)):  # extrae el indice de la lista
            if auxFiles[x] == indexName[0]:
                auxFiles.pop(x)
                break
        indexPath = self.indice
        try:
            wb = xw.Book(indexPath)
            app = wb.app
            app.visible = False  # Hacer que la aplicación de Excel no sea visible
            macro_vba = app.macro(
                "'" + str(os.path.basename(self.indice)) + "'" + "!Macro1InsertarFila"
            )
            sheet = wb.sheets.active
        except Exception:
            print("Excepcion presentada al intentar acceder al indice electronico\n")
            traceback.print_exc()
        df = self.createDataFrame(self.files, self.ruta)
        self.createXlsm(df, macro_vba, sheet)
        wb.save()
        wb.close()
        # wb.app.quit()
        return 1

    def createXlsm(self, df, macro_vba, sheet):
        """
        @param: df; contiene DataFrame con datos a registrar en excel
        @return:
        @modules: xlwings

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
        # filaFinal = filaInicial + df.shape[0]
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
