""" 
- Esta clase se encarga de manejar la interacción entre el modelo y la vista
- ControladorExpediente maneja la lógica de negocio relacionada con los expedientes y actualiza la vista en consecuencias
- Controla las configuraciones del programa para gestionar entre otros la cantidad de dígitos del consecutivo conectado con la vista y el modelo
"""

class Main_controller:
    
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

    