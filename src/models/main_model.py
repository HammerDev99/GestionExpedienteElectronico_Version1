""" Esta clase gestiona los datos y la lógica de negocio, entre otros, la lógica para manejar los archivos del expediente electronico """

class Main_model():

    def leer_archivo(): # para leer los metadatos de un archivo.
        pass

    def modificar_nombre_archivo(): # para modificar el nombre de un archivo.
        pass

    def leer_excel(): # para leer los datos de un archivo de Excel.
        pass
    
    def escribir_excel(): # para escribir los datos en un archivo de Excel.
        pass

    def cantidad_digitos_consecutivo(): # Para controlar la cantidad de digitos del consecutivo
        pass

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
                    #number_of_strings = 3
                    length_of_string = 3
                    os.rename(ruta + chr(92) + files[i], ruta + chr(92) + os.path.splitext(nombresExtensiones[i])[0] + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length_of_string)) + os.path.splitext(nombresExtensiones[i])[1])
                except:
                    print("Excepcion presentada: \n")

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

    def isOrderCorrect(self, files, nombresExtensiones):
        """ 
        @param: files, nombresExtensiones
        @return: Bool
        - Verifica el orden de los consecutivos de los archivos
        """

        cont = 0
        for i in files:
            for j in nombresExtensiones:
                if i!=j:
                    cont = cont + 1
        if cont!=0:
            return True
        else:
            return False

    def fullFilePath(self, files, ruta):
        """ 
        @param: files (List); ruta (string)
        @return: pathArchivos tipo List
        """

        pathArchivos = []
        for y in files:
            fulldirct = os.path.join(ruta, y)
            fulldirct.replace("/","\\")
            pathArchivos.append(fulldirct)
        return pathArchivos


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

