class Main_controller:
    """ Controlador principal 
    
    - Se encarga de manejar la interacción entre el modelo y la vista
    - Maneja la lógica de negocio relacionada con los expedientes y actualiza la vista en consecuencia
    - Se encarga de la captura y edición de archivos por tratarse de la interacción del usuario con la aplicación
    - Controla las configuraciones del programa para gestionar entre otros la cantidad de dígitos del consecutivo conectado con la vista y el modelo

    Attributes:
        abcdef
    """

    def __init__(self, model, view):
        """ Inicializa el controlador
        
        Args:
            model: Main_model
            view: Main_view
        
        Returns:
            None

        Raises:
            None
        """
        self.model = model
        self.view = view
    
    # ________________________ código refactorizado ⬆️ (Pendiente ⬇️)

    def obtenerExpediente(self):
        """ 
        - Obtiene ruta seleccionada por usuario, 
        Actualiza variable global expediente
        Ejecuta funcion agregaNombreBase enviando la ruta y parametro False
         """

        folder_selected = filedialog.askdirectory()
        self.expediente = folder_selected
        self.agregaNombreBase(folder_selected, False)
        
    def mensaje(self, result):
        """ 
        @param: result tipo int
        @modules: tkinter
        - Utiliza la GUI para enviar mensaje
         """
        switcher={
                0:'Procedimiento detenido. No se encontraron los archivos indicados en el índice',
                1:'Procedimiento finalizado',
                2:'Archivos sin procesar',
                3:'Seleccione una carpeta para procesar',
                4:'Agregue archivos a la lista',
                5:'La carpeta electrónica del expediente se encuentra actualizada',
                6:'Procedimiento detenido'
             }
        if result != None:
            tk.messagebox.showinfo(message=switcher.get(result), title=os.path.basename(self.expediente))
    
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
            #self.listaNombres = nombres
        else:
            self.entry1.config(state=tk.NORMAL)
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, items)
            self.entry1.config(state=tk.DISABLED)

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

    # Posibles funciones futuras
    
    def seleccionar_archivo(): # para seleccionar un archivo o varios archivos.
        pass

    def mostrar_tabla(): # para mostrar los datos en una tabla.
        pass

    def mostrar_error(): # para mostrar mensajes de error en la interfaz de usuario.
        pass

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

    def manejo_archivos_multipltaforma():
        # import os

        # Obtener la ruta actual del archivo
        current_dir = os.getcwd()

        # Unir dos partes de una ruta de archivo
        file_path = os.path.join(current_dir, 'data', 'file.txt')

        # Abrir un archivo en modo lectura en una forma multiplataforma
        with open(file_path, 'r', newline='', encoding='utf-8') as file:
            # Hacer algo con el archivo
            pass

        # Crear una carpeta en una forma multiplataforma
        new_dir = os.path.join(current_dir, 'output')
        os.makedirs(new_dir, exist_ok=True)

        # Crear un archivo en una forma multiplataforma
        new_file_path = os.path.join(new_dir, 'new_file.txt')
        with open(new_file_path, 'w', newline='', encoding='utf-8') as file:
            # Escribir algo en el archivo
            file.write('Hola, mundo!\n')

        # Copiar el archivo 
        # import shutil
        # Rutas de archivo origen y destino
        source_file = os.path.join(current_dir, 'data', 'source.txt')
        dest_file = os.path.join(current_dir, 'output', 'dest.txt')

        # Copiar el archivo
        shutil.copy(source_file, dest_file)