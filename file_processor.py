# coding=utf-8
# Empleado
import os
import sys
import psutil
import pandas as pd
import shutil
import xlwings as xw
import string
import random
import traceback
from metadata_extractor import MetadataExtractor
import logging

class FileProcessor:

    ruta = ""
    indice = ""
    files = []
    pids_creados = []

    obj1 = None

    def __init__(self, input: str, indice, despacho, subserie, rdo, logger=None):
        # @param: input tipo str; Obtiene ruta de la carpeta a procesar
        self.logger = logger or logging.getLogger('GestionExpediente.file_processor')
        self.logger.info(f"Iniciando procesamiento para expediente: {input}")
        
        self.obj1 = MetadataExtractor(logger=self.logger)

        try:
            self.ruta = input
            self.files = os.listdir(self.ruta)
            self.logger.debug(f"Archivos encontrados: {len(self.files)}")

            if indice == "":
                self.copyXlsm(self.ruta)
            else:
                self.indice = indice

            self.despacho = despacho
            self.subserie = subserie
            self.rdo = rdo
            
        except Exception as e:
            self.logger.error(f"Error en inicialización: {str(e)}", exc_info=True)
            raise

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

        self.logger.info(f"Renombrando {len(files)} archivos en {ruta}")
        for i in range(len(files)):
            try:
                fulldirct = os.path.join(ruta, files[i])
                self.logger.debug(f"Renombrando: {fulldirct}")
                if os.path.exists(fulldirct):
                    os.rename(fulldirct, os.path.join(ruta, nombresExtensiones[i]))
                else:
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
            except Exception as e:
                self.logger.error(f"Error renombrando archivo: {str(e)}", exc_info=True)
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
            self.logger.error("Excepcion presentada al intentar acceder al indice electronico", exc_info=True)
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

    def cerrar_procesos_por_pid(self, pids):
        """
        Cierra los procesos especificados en la lista de PID.
        @param: pids tipo list; lista de PID de los procesos a cerrar
        """
        for pid in pids:
            self.logger.info(f"Cerrando proceso con PID {pid}")
            try:
                proc = psutil.Process(pid)
                proc.kill()  # forzar el cierre
                print(f"Proceso {proc.name()} con PID {pid} cerrado.")
                self.pids_creados.remove(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                print(f"No se pudo cerrar el proceso con PID {pid}: {e}")
                self.logger.error(f"No se pudo cerrar el proceso con PID {pid}: {e}")