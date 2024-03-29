# coding=utf-8

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
import sys
import webbrowser
from automatizacionEmpleado import AutomatizacionEmpleado

class Application(ttk.Frame):

    expediente = ''
    
    def __init__(self, root):

        super().__init__(root)
        root.title('GestionExpedienteElectronico')
        root.resizable(False, False)
        root.geometry('350x165')
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.create_oneProcessWidgets()

    def create_oneProcessWidgets(self):
        """ 
        ### GUI GestionExpedienteElectronico_Version1
         """

        self.label = tk.Label(self, text=r"HammerDev99", fg="blue", cursor="hand2")
        self.label.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label.bind("<Button-1>", lambda e: self.callback("https://github.com/HammerDev99/GestionExpedienteElectronico_Version1"))

        self.label1 = tk.Label(self, text='Seleccione la carpeta del expediente electrónico')
        self.label1.pack(pady=15)
        
        self.scrollbar = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.scrollbar.pack(fill="x", padx=5)

        self.entry1 = tk.Entry (self, width = 50, xscrollcommand=self.scrollbar.set)
        self.entry1.config(state=tk.DISABLED)
        self.entry1.insert("end", str(dir(tk.Scrollbar)))
        self.entry1.pack(fill="x", before=self.scrollbar)
        
        self.scrollbar.config(command=self.entry1.xview)

        self.pathExpediente = tk.Button(self, text = 'Agregar carpeta', command = self.obtenerExpediente, height = 1, width = 17)
        self.pathExpediente.pack(side=tk.LEFT)

        self.label5 = tk.Label(self, text='')
        self.label5.pack(side=tk.LEFT)

        self.aceptar = tk.Button(self, text = 'Aceptar', command = self.procesaCarpeta, height = 1, width = 7)
        self.aceptar.pack(side=tk.RIGHT, padx=3)

        self.cancelar = tk.Button(self, text = 'Cancelar', fg = 'red', command = self.on_closing, height = 1, width = 7)
        self.cancelar.pack(side=tk.RIGHT, before=self.aceptar)

        self.pack()

    def callback(self, url):
        """
        @modules: webbrowser 
        """
        webbrowser.open_new(url)

    def on_closing(self):
        print('Cerrando aplicación')
        root.destroy()
        #root.quit()

    def obtenerExpediente(self):
        """ 
        - Obtiene ruta seleccionada por usuario, 
        Actualiza variable global expediente
        Ejecuta funcion agregaNombreBase enviando la ruta y parametro False
         """

        folder_selected = os.path.normpath(filedialog.askdirectory())
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
                6:'Procedimiento detenido'
             }
        if result != None:
            tk.messagebox.showinfo(message=switcher.get(result), title=os.path.basename(self.expediente))
            lista_vacia = list()
            self.agregaNombreBase(lista_vacia, False)

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

# Quitar comentario si se ejecuta desde el __main__.py
            
root = tk.Tk()
app = Application(root)
app.mainloop()

# Punto de entrada sin __main__.py
""" if __name__ == '__main__':
    root = tk.Tk()
    obj = Application(root)
    root.mainloop() """