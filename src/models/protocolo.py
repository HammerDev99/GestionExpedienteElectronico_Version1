""" Esta clase se encarga de aplicar las reglas del protocolo y de gestionar los datos relevantes de cada archivo """

class Protocolo():

    def __init__(self) -> None:
        super().__init__()
        self.ruta = ""
        self.nombre = ""
        self.fecha = ""
        self.posicion = ""
        self.paginas = ""
        self.extension = ""
        self.tamano = ""
        self.origen = ""
        self.observaciones = ""

    # ________________________ código refactorizado ⬆️ (Pendiente ⬇️)

    def get_ruta(self):
        return self.ruta

    def set_ruta(self, ruta):
        self.ruta = ruta

    def get_nombre(self):
        return self.nombre

    def set_nombre(self, nombre):
        self.nombre = nombre

    def get_fecha(self):
        return self.fecha

    def set_fecha(self, fecha):
        self.fecha = fecha

    def get_posicion(self):
        return self.posicion

    def set_posicion(self, posicion):
        self.posicion = posicion

    def get_paginas(self):
        return self.paginas

    def set_paginas(self, paginas):
        self.paginas = paginas

    def get_extension(self):
        return self.extension

    def set_extension(self, extension):
        self.extension = extension

    def get_tamano(self):
        return self.tamano

    def set_tamano(self, tamano):
        self.tamano = tamano

    def get_origen(self):
        return self.origen

    def set_origen(self, origen):
        self.origen =origen

    def get_observaciones(self):
        return self.observaciones

    def set_observaciones(self, observaciones):
        self.observaciones = observaciones
            
    def formatNames(self, ruta, files): 
        """ 
        @param: ruta, files
        @return: nombresExtensiones, nombres, extensiones, numeraciones, ban
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

        nombres = []
        extensiones = []
        for x in files:
            fulldirct = os.path.join(ruta, x)
            if os.path.isfile(fulldirct):
                nombres.append(os.path.splitext(x)[0])
                extensiones.append(os.path.splitext(x)[1])
            else: 
                nombres.append(x)
                extensiones.append('Carpeta')
                
        ban = False
        for x in range(len(nombres)):
            if not(nombres[x].isalnum()) or len(nombres[x])>40:
                nombres[x] = string.capwords(nombres[x])
                result = re.sub('[^a-zA-Z0-9]+', '', nombres[x])
                nombres[x] = result
                ban=True
            else:
                # Entran los archivos sin extensión
                #print("entró: ",nombres[x])
                pass
            cont = 0
            for caracter in nombres[x]:
                if caracter.isalpha():
                    nombres[x] = nombres[x][cont:]
                    break
                else:
                    if caracter.isnumeric():
                        cont = cont +1
                        continue
            nombres[x] = nombres[x][0:36]
            if nombres[x] == "":
                nombres[x] = ("DocumentoElectronico")
            nombres[x] = str(f"{x+1:03}")+nombres[x]
        nombresExtensiones=[]
        for x in range(len(nombres)):
            if extensiones[x] != 'Carpeta':
                nombresExtensiones.append(str(nombres[x])+str(extensiones[x]))
            else:
                nombresExtensiones.append(str(nombres[x]))
        numeraciones = list(range(len(nombres)+1))
        numeraciones.pop(0)
        if self.isOrderCorrect(files, nombresExtensiones):
            ban = True
        return nombresExtensiones, nombres, extensiones, numeraciones, ban
    
    def sizeUnitsConverter(self, size): 
        """ 
        @param: size of a file
        @return: string; contiene cantidad mas unidad de medicion
        """

        kb=1024;
        bytes = kb / 1024;
        mb=kb*1024;
        gb=mb*1024;
        tb=gb*1024;
        if size>=tb:
            return "%.1f TB"% float(size / tb)
        if size>=gb:
            return "%.1f GB"% float(size / gb)
        if size>=mb:
            return "%.1f MB"% float(size / mb)
        if size>=kb:
            return "%.1f KB"% float(size / kb)
        if size<kb:
            return "%.0f BYTES"% float(size / bytes)
        if size==0:
            return ('0 BYTES')

    def pageCounter(self, file):
        """ 
        @param: file (string)
        @return: int; cantidad de paginas 
        @modules: PyPDF2, warnings, os, sys
         """

        path, extension = os.path.splitext(file)
        extension = extension.lower()
        if os.path.isfile(file):
            if extension == '.pdf':
                with open(file,'rb') as f:
                    try:
                        pdf = PyPDF2.PdfFileReader(f)
                        if not sys.warnoptions:
                            warnings.simplefilter("ignore")
                        return pdf.getNumPages()
                    except:
                        return 0
            elif (extension == '.xls' or extension == '.xlsx' or extension == '.xlsm' or
                extension == '.bmp' or extension == '.jpeg' or extension == '.jpg' or extension == '.mp4' or
                extension == '.png' or extension == '.tif' or extension == '.textclipping' or
                extension == '.wmv' or extension == '.eml' or extension == '.txt' or extension == '.gif' or 
                extension == '.html'):
                return(1)
            else:
                return(0)
        else:
            return(1)
        
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

        #*********************************************
        #Separar instrucciones en funcion a parte
        nombresExtensiones, nombres, extensiones, numeraciones, ban = self.obj1.formatNames(ruta, files)
        if ban: 
            self.renameFiles(files, nombresExtensiones, ruta)
        fullFilePaths = self.fullFilePath(nombresExtensiones, ruta)

        fechamod, tama, cantidadpag, observaciones = self.obj1.getMetadata(fullFilePaths)
        #*********************************************
        df = pd.DataFrame()
        df['Nombre documento'] = None
        df['Fecha'] = None
        df['Orden'] = None
        df['Paginas'] = None
        df['Formato'] = None
        df['Tamaño'] = None
        df['Origen'] = None
        df['Observaciones'] = None
        for y in range(len(nombres)):  
            nueva_fila = pd.Series([str(nombres[y]), str(fechamod[y]), str(numeraciones[y]), str(cantidadpag[y]), str(extensiones[y].replace('.',"")), str(tama[y]), 'Electrónico', str(observaciones[y])], index=df.columns)
            df = df.append(nueva_fila, ignore_index=True)
        return df