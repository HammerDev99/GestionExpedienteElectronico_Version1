#pip install pyPDF2

import datetime
import re
import os
import string
import sys
import warnings
import PyPDF2 

class AutomatizacionData:

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
                number_files = len(list_files)
                nombres, extensiones = self.separatePath(list_files)
                nombresExtensiones, nombres, extensionesR, numeraciones = self.formatNames(x, list_files)
                self.renameFiles(list_files, nombresExtensiones, x)
                observaciones.append('Número de archivos contenidos: '+str(number_files)+'. Formatos: '+str(extensiones))
        return fechamod, tama, cantidadpag, observaciones

    # VALIDAR ERROR CUANDO LOS NOMBRES SEAN DE SOLO NUMEROS
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
            nombres[x] = str(f"{x+1:04}")+nombres[x]
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
            elif extension == '.xls' or extension == '.xlsx' or extension == '.xlsm':
                return(1)
            elif (extension == '.bmp' or extension == '.jpeg' or extension == '.jpg' or extension == '.mp4' or
                extension == '.png' or extension == '.tif' or extension == '.textclipping' or
                extension == '.wmv' or extension == '.eml' or extension == '.txt' or extension == '.gif' or 
                extension == '.html'):
                return(1)
            else:
                return(0)
        else:
            return(1)