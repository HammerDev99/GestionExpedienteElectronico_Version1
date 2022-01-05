#pip install tk

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
from AutomatizacionEmpleado import AutomatizacionEmpleado

class Application(ttk.Frame):

    expediente = ''
    
    def __init__(self, main_window):

        super().__init__(main_window)
        main_window.title('GestionExpedienteElectronico')
        main_window.resizable(False, False)
        main_window.geometry('300x160')
        self.create_oneProcessWidgets()

    
    def create_oneProcessWidgets(self):
        """ 
        - GUI GestionExpedienteElectronico_Version1
         """
        self.label4 = tk.Label(self)
        self.label4.pack(side = tk.TOP)
        self.label1 = tk.Label(self, text='Crear índice del expediente electrónico')
        self.label1.pack(side = tk.TOP)
        self.label2 = tk.Label(self, text='')
        self.label2.pack(side = tk.BOTTOM)
        self.entry1 = tk.Entry (self, width = 40)
        self.entry1.config(state=tk.DISABLED)
        self.entry1.pack(side = tk.TOP)
        self.pathExpediente = tk.Button(self, text = 'Seleccionar expediente', command = self.obtenerExpediente, height = 1, width = 17)
        self.pathExpediente.pack(side = tk.TOP)
        self.cancelar = tk.Button(self, text = 'Cancelar', fg = 'red', command = self.master.destroy, height = 1, width = 7)
        self.cancelar.pack(side = tk.BOTTOM)
        self.aceptar = tk.Button(self, text = 'Procesar', command = self.procesaCarpeta, height = 1, width = 7)
        self.aceptar.pack(side = tk.BOTTOM)
        self.pack()

    def obtenerExpediente(self):
        """ 
        - Obtiene ruta seleccionada por usuario, 
        Actualiza variable global expediente
        Ejecuta funcion agregaNombreBase enviando la ruta y parametro False
         """

        folder_selected = filedialog.askdirectory()
        self.expediente = folder_selected
        self.agregaNombreBase(folder_selected, False)

    def procesaCarpeta(self):
        """ 
        - Crea objeto y llama metodo process()
         """
        if self.expediente != '':
                if tk.messagebox.askyesno(message="Se procesarán los archivos que contiene la carpeta \""+ os.path.basename(self.expediente) +"\". \n¿Desea continuar?.", title=os.path.basename(self.expediente)):
                    obj = AutomatizacionEmpleado(self.expediente, "")
                    self.mensaje(obj.process())
                else:
                    self.mensaje(6)
        else:
            self.mensaje(3)

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
                6:'Procesamiento detenido'
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

main_window = tk.Tk()
app = Application(main_window)
app.mainloop()