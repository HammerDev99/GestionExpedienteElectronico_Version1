# coding=utf-8

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
import sys
import webbrowser
from automatizacionEmpleado import AutomatizacionEmpleado

class Application(ttk.Frame):

    expediente = ""

    def __init__(self, root):

        super().__init__(root)
        root.title("GestionExpedienteElectronico")
        root.resizable(False, False)
        #root.geometry("350x300")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pack(padx=20, pady=20)  # Añadir padding aquí
        self.create_oneProcessWidgets()

    def create_oneProcessWidgets(self):
        """
        ### GUI GestionExpedienteElectronico_Version1
        """

        self.label = tk.Label(self, text=r"Daniel Arbelaez Alvarez - HammerDev99", fg="blue", cursor="hand2")
        self.label.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label.bind(
            "<Button-1>",
            lambda e: self.callback(
                "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1"
            ),
        )

        self.label01 = tk.Label(
            self, text="Juzgado"
        )
        self.label01.pack(pady=5)

        self.entry01 = tk.Entry(self, width=50)
        self.entry01.pack(pady=5)
        self.entry01.insert(0, "JUZGADO TERCERO CIVIL MUNICIPAL DE BELLO")

        self.label02 = tk.Label(
            self, text="Serie o Subserie"
        )
        self.label02.pack(pady=5)

        self.entry02 = tk.Entry(self, width=50)
        self.entry02.pack(pady=5)
        self.entry02.insert(0, "Expedientes de Procesos Judiciales Ejecutivos")

        self.label1 = tk.Label(
            self, text="Seleccione la ubicación de la subserie a procesar \n(Debe contener expedientes)"
        )
        self.label1.pack(pady=15)

        """ self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(fill="x", padx=5) """
        #self.scrollbar.config(command=self.entry1.xview)
        # Crear una barra de desplazamiento vertical
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        """ self.entry1 = tk.Entry(self, width=50, xscrollcommand=self.scrollbar.set)
        self.entry1.config(state=tk.DISABLED)
        self.entry1.insert("end", str(dir(tk.Scrollbar)))
        self.entry1.pack(fill="x", before=self.scrollbar) """
        # Crear un Text widget para mostrar los RDOs procesados
        self.text_widget = tk.Text(self, width=50, height=10, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # Configurar la barra de desplazamiento para el Text widget
        self.scrollbar.config(command=self.text_widget.yview)


        self.pathExpediente = tk.Button(
            self,
            text="Procesar carpeta",
            #command=self.obtenerExpediente,
            command=self.obtenerExpedientes,
            height=1,
            width=17,
        )
        self.pathExpediente.pack(side=tk.LEFT)

        self.label5 = tk.Label(self, text="")
        self.label5.pack(side=tk.LEFT)

        self.aceptar = tk.Button(
            #self, text="Aceptar", command=self.procesaCarpeta, height=1, width=7
            self, text="Aceptar", command=self.procesaCarpetas, height=1, width=7
        )
        #self.aceptar.pack(side=tk.RIGHT, padx=3)

        self.cancelar = tk.Button(
            self, text="Cancelar", fg="red", command=self.on_closing, height=1, width=7
        )
        #self.cancelar.pack(side=tk.RIGHT, before=self.aceptar)
        self.cancelar.pack(side=tk.RIGHT, before=self.pathExpediente)

        self.pack()

    def callback(self, url):
        """
        @modules: webbrowser
        """
        webbrowser.open_new(url)

    def on_closing(self):
        print("Cerrando aplicación")
        root.destroy()
        # root.quit()

    def obtenerExpediente(self):
        """
        - Obtiene ruta seleccionada por usuario,
        Actualiza variable global expediente
        Ejecuta funcion agregaNombreBase enviando la ruta y parametro False
        """

        folder_selected = os.path.normpath(filedialog.askdirectory())
        self.expediente = folder_selected
        self.agregaNombreBase(folder_selected, False)

    def obtenerExpedientes(self):
        """
        - Obtiene la ruta seleccionada por el usuario,
        - Recupera la lista de carpetas en esa ruta,
        - Llama a procesaCarpetas con la lista de carpetas
        """
        folder_selected = os.path.normpath(filedialog.askdirectory())
        if folder_selected:
            carpetas = [os.path.join(folder_selected, d) for d in os.listdir(folder_selected) if os.path.isdir(os.path.join(folder_selected, d))]
            self.procesaCarpetas(carpetas)
            self.mensaje(1)

    def procesaCarpetas(self, carpetas):
        """
        - Crea objeto y llama metodo process() para cada carpeta en la lista
        """
        self.text_widget.insert(tk.END, f"CARPETAS PROCESADAS:\n")
        for carpeta in carpetas:
            despacho = self.entry01.get()
            subserie = self.entry02.get()
            rdo = os.path.basename(carpeta)

            print("Despacho: ", despacho)
            print("Subserie: ", subserie)
            print("RDO: ", rdo)
            self.text_widget.insert(tk.END, f"{rdo}\n")
            self.text_widget.see(tk.END)

            obj = AutomatizacionEmpleado(carpeta, "", despacho, subserie, rdo)
            result = obj.process()

    def procesaCarpeta(self):
        """
        - Crea objeto y llama metodo process()
        """
        if self.expediente != "":
            if tk.messagebox.askyesno(
                message='Se procesarán los archivos que contiene la carpeta "'
                + os.path.basename(self.expediente)
                + '". \n¿Desea continuar?.',
                title=os.path.basename(self.expediente),
            ):
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
        switcher = {
            0: "Procedimiento detenido. No se encontraron los archivos indicados en el índice",
            1: "Procedimiento finalizado",
            2: "Archivos sin procesar",
            3: "Seleccione una carpeta para procesar",
            4: "Agregue archivos a la lista",
            5: "La carpeta electrónica del expediente se encuentra actualizada",
            6: "Procedimiento detenido",
        }
        if result != None:
            tk.messagebox.showinfo(
                message=switcher.get(result), title=os.path.basename(self.expediente)
            )
            #self.text_widget.insert(tk.END, switcher.get(result))
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
            # self.listaNombres = nombres
        else:
            """ self.entry1.config(state=tk.NORMAL)
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, items)
            self.entry1.config(state=tk.DISABLED) """


# Quitar comentario si se ejecuta desde el __main__.py

root = tk.Tk()
app = Application(root)
app.mainloop()

# Punto de entrada sin __main__.py
""" if __name__ == '__main__':
    root = tk.Tk()
    obj = Application(root)
    root.mainloop() """
