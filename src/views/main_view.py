""" Esta clase se encarga de gestionar la interfaz de usuario, contiene la interfaz gráfica de usuario para seleccionar archivos y mostrar los resultados """

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser

class Gui(ttk.Frame):

    def __init__(self, root):
        super().__init__(root)
        root.title('GestionExpedienteElectronico')
        root.resizable(False, False)
        root.geometry('350x165')
        self.create_oneProcessWidgets()

    # ________________________ Separa código refactorizado ⬆️ (Pendiente ⬇️)
    
    def create_oneProcessWidgets(self):
        """ 
        GUI GestionExpedienteElectronico_Version1
        """

        #Crear widgets para la cantidad de dígitos del consecutivo

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

        self.cancelar = tk.Button(self, text = 'Cancelar', fg = 'red', command = self.master.destroy, height = 1, width = 7)
        self.cancelar.pack(side=tk.RIGHT, before=self.aceptar)

        self.pack()

    def callback(self, url):
        """
        @modules: webbrowser 
        """

        webbrowser.open_new(url)
    
root = tk.Tk()
app = Gui(root)
app.mainloop()