
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import webbrowser

class MainView(tk.Frame):
    """ Esta clase se encarga de gestionar las diferentes interfaces gráficas de usuario """

    def __init__(self):
        self.root = tk.Tk()
        # Crear instancias de las vistas
        self.view1 = View1(self.root)
        # Llamar al método que configura los eventos
        self.setup_events()
        # Ejecuta la función run()
        self.run()

    def run(self):
        self.root.mainloop()

    def setup_events(self):
        # Configurar los eventos de las vistas
        #self.view1.on_button_click = self.handle_view1_button_click
        pass

    def handle_view1_button_click(self, event):
        # Lógica de la aplicación para el botón de la vista 1
        pass

class View1(tk.Frame):
    """ Esta clase se encarga de gestionar la interfaz de usuario, contiene la vista 1 para seleccionar la carpeta y generar el índice """

    def __init__(self, parent):
        super().__init__(parent)
        
        #Crear widgets para la cantidad de dígitos del consecutivo
        
        """ self.label = tk.Label(self, text=r"HammerDev99", fg="blue", cursor="hand2")
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

        self.pathExpediente = tk.Button(self, text = 'Agregar carpeta', command = None , height = 1, width = 17) # self.obtenerExpediente
        self.pathExpediente.pack(side=tk.LEFT)

        self.label5 = tk.Label(self, text='')
        self.label5.pack(side=tk.LEFT)

        self.aceptar = tk.Button(self, text = 'Aceptar', command = None, height = 1, width = 7) # self.procesaCarpeta
        self.aceptar.pack(side=tk.RIGHT, padx=3)

        self.cancelar = tk.Button(self, text = 'Cancelar', fg = 'red', command = self.master.destroy, height = 1, width = 7)
        self.cancelar.pack(side=tk.RIGHT, before=self.aceptar) """

        self.button = tk.Button(self, text="Click me!")
        self.button.pack()

        self.master.title('GestionExpedienteElectronico')
        self.master.resizable(False, False)
        self.master.geometry('350x165')

        """ 

        # Evento personalizado
        self.on_button_click = None

        # Llamar al método que configura los eventos
        self.setup_events() """

    def setup_events(self):
        self.button.bind("<Button-1>", self.button_click)

    def button_click(self, event):
        if self.on_button_click:
            self.on_button_click(event)
    
    # ________________________ código refactorizado ⬆️ (Pendiente ⬇️)

    def callback(self):
        """
        @modules: webbrowser 
        """
        
        url = "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1"
        webbrowser.open_new(url)