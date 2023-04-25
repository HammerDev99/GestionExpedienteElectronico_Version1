
class MainModel():
    """ Esta clase gestiona los datos y la lógica de negocio, entre otros, la lógica para manejar los archivos del expediente electronico, es decir, va a orquestar el entre el índice del expediente y el protocolo de expediente """

    def __init__(self):
        pass

    # ________________________ código refactorizado ⬆️ (Pendiente ⬇️)

    # Probar usando el modulo OpenPyXl para manipular los archivos de excel
    # https://programacion.net/articulo/como_trabajar_con_archivos_excel_utilizando_python_1419
    # https://openpyxl.readthedocs.io/en/stable/editing_worksheets.html?highlight=insert%20row
    def process(self):
        """ 
        @return: int
        @modules: xlwings
        """

        auxFiles, extension = self.separatePath(self.files) # datos en variales files
        listAux = [os.path.basename(self.indice)] # datos en carpeta
        indexName, indexExtension = self.separatePath(listAux)
        for x in range(len(auxFiles)): # extrae el indice de la lista
            if auxFiles[x] == indexName[0]:
                auxFiles.pop(x)
                break
        indexPath = self.indice
        try:
            wb = xw.Book(indexPath) 
            app = wb.app 
            macro_vba = app.macro("'"+str(os.path.basename(self.indice))+"'"+"!Macro1InsertarFila")
            sheet = xw.sheets.active
        except Exception:
            print("Excepcion presentada al intentar acceder al indice electronico\n")
            traceback.print_exc()
        df = self.createDataFrame(self.files, self.ruta)
        self.createXlsm(df, macro_vba, sheet)
        wb.save()
        #wb.close()
        return 1

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
                observaciones.append('')
            else:
                fechamod.append(str(datetime.date.fromtimestamp(os.path.getmtime(x))))
                tama.append('-')
                cantidadpag.append('1')
                list_files = os.listdir(x)
                nombres, extensiones = self.separatePath(list_files)
                comments = dict(zip(extensiones,map(lambda x: extensiones.count(x),extensiones))) # combinar los valores para posteriormente pasarlo a un diccionario. Utilizamos map() y le aplicamos una lambda esta lambda obtendrá la veces que se repite un valor, esto para cada valer de la lista. Luego se utiliza zip() para mezclar ambos datos y obtener una tapa para posteriormente pasarlo a un diccionario.
                nombresExtensiones, nombres, extensionesR, numeraciones, ban = self.formatNames(x, list_files)
                self.renameFiles(list_files, nombresExtensiones, x)
                observaciones.append('Archivos contenidos: ' + str(comments))
        return fechamod, tama, cantidadpag, observaciones

    # Posibles funciones futuras

