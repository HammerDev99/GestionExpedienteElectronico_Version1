# coding=utf-8

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
import sys
import webbrowser
import requests
import json
from automatizacionEmpleado import AutomatizacionEmpleado

class Application(ttk.Frame):

    expediente = ""
    carpetas = []
    is_updated = True

    def __init__(self, root, is_updated=True):
        """
        @param: root tipo Tk; contiene la raíz de la aplicación Tkinter
        @modules: tkinter
        - Inicializa la aplicación, configura la ventana principal y crea los widgets.
        """

        super().__init__(root)
        root.title("GestionExpedienteElectronico")
        root.resizable(False, False)
        # root.geometry("350x300")
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.pack(padx=20, pady=20)  # Añadir padding aquí
        self.create_oneProcessWidgets()

    def create_oneProcessWidgets(self):
        """
        @modules: tkinter
        - Crea y configura los widgets de la interfaz gráfica.
        """
        self.is_updated = self.comprobar_actualizaciones() # Comprobar actualizaciones al iniciar la aplicación

        self.label = tk.Label(self, text=r"Daniel Arbelaez Alvarez - HammerDev99", fg="blue", cursor="hand2")
        self.label.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label.bind(
            "<Button-1>",
            lambda e: self.callback(
                "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1"
            ),
        )

        if not self.is_updated:
            # Crear un contenedor para el label de actualización
            self.update_frame = tk.Frame(self)
            self.update_frame.pack(side=tk.TOP, fill=tk.X)

            self.update_label = tk.Label(
                self.update_frame, text="🚀 Nueva versión disponible", fg="green", cursor="hand2"
            )
            self.update_label.pack(side=tk.RIGHT, padx=0, pady=0)
            self.update_label.bind(
                "<Button-1>",
                lambda e: self.callback(
                    "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/latest"
                ),
            )

        self.label01 = tk.Label(
            self, text="Juzgado", 
            font=("Helvetica", 12)
        )
        self.label01.pack(pady=5)

        self.entry01 = tk.Entry(self, width=50)
        self.entry01.pack(pady=5)
        self.entry01.insert(0, "CENTRO DE SERVICIOS JUDICIALES DE BELLO")

        self.label02 = tk.Label(
            self, text="Serie o Subserie", 
            font=("Helvetica", 12)
        )
        self.label02.pack(pady=5)

        self.entry02 = tk.Entry(self, width=50)
        self.entry02.pack(pady=5)
        self.entry02.insert(0, "Expedientes de Procesos Judiciales")

        # Label y entry para la variable rdo
        self.label03 = tk.Label(
            self, text="Radicado", 
            font=("Helvetica", 12)
        )
        self.label03.pack(pady=5)

        self.entry03 = tk.Entry(self, width=50)
        self.entry03.pack(pady=5)
        self.entry03.insert(0, "")

        self.label1 = tk.Label(
            self, text="(Dejar en blanco si el nombre de las subcarpetas corresponde al número de radicado)", 
            font=("Helvetica", 11)
        )
        self.label1.pack(pady=1)

        """ self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(fill="x", padx=5) """
        # self.scrollbar.config(command=self.entry1.xview)
        # Crear una barra de desplazamiento vertical
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        """ self.entry1 = tk.Entry(self, width=50, xscrollcommand=self.scrollbar.set)
        self.entry1.config(state=tk.DISABLED)
        self.entry1.insert("end", str(dir(tk.Scrollbar)))
        self.entry1.pack(fill="x", before=self.scrollbar) """
        # Crear un Text widget para mostrar los RDOs procesados
        self.text_widget = tk.Text(self, width=50, height=20, yscrollcommand=self.scrollbar.set)
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        self.text_widget.insert(tk.END, "Instrucciones de Uso del Programa\n\n- Descargar la Carpeta: Descarga las carpetas que deben contener archivos, sin incluir ningún índice.\n\n- Nombrar la Carpeta: Asegúrate de que la carpeta del expediente tenga el radicado de 23 dígitos y los archivos estén ordenados dentro.\n\n- Verificar Metadatos: Las fechas de creación y modificación de los archivos reflejarán las del archivo descargado.\n\n- Cerrar Excel: Asegúrate de que todos los archivos de Excel estén cerrados antes de ejecutar el programa.\n\n- CARPETA: La carpeta seleccionada deberá tener la siguiente estructura carpeta_seleccionada/subcarpeta/archivos_para_indice.\n\n- Inicio Automático: El programa comenzará a procesar automáticamente UNA VEZ SELECCIONE la carpeta a procesar.\n\n")

        # Configurar la barra de desplazamiento para el Text widget
        self.scrollbar.config(command=self.text_widget.yview)

        self.pathExpediente = tk.Button(
            self,
            text="Agregar carpeta",
            command=self.obtenerExpedientes,
            height=1,
            width=17,
        )
        self.pathExpediente.pack(side=tk.LEFT, padx=5)

        # Barra de progreso
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=5)

        # Botón Aceptar
        self.aceptar = tk.Button(
            self, text="Aceptar", command=self.procesaCarpetas, height=1, width=7
        )
        self.aceptar.pack(side=tk.LEFT, padx=5)

        # Botón Cancelar
        self.cancelar = tk.Button(
            self, text="Cancelar", fg="red", command=self.on_closing, height=1, width=7
        )
        self.cancelar.pack(side=tk.LEFT, padx=5)

        # Otros widgets...
        self.label5 = tk.Label(self, text="")
        self.label5.pack(side=tk.LEFT)

        self.pack()

    def callback(self, url):
        """
        @modules: webbrowser
        """
        webbrowser.open_new(url)

    def on_closing(self):
        """
        @modules: tkinter
        - Maneja el evento de cierre de la ventana principal.
        """
        print("Cerrando aplicación")
        root.destroy()
        # root.quit()

    # Funcion para el caso de una carpeta (2 niveles: carpeta/archivos)
    def obtenerExpediente(self):
        """
        - Obtiene ruta seleccionada por usuario
        - Actualiza variable global expediente
        - Ejecuta funcion agregaNombreBase enviando la ruta y parametro False
        """

        folder_selected = os.path.normpath(filedialog.askdirectory())
        self.expediente = folder_selected
        self.agregaNombreBase(folder_selected, False)

    # Funcion para el caso de varias carpetas (3 niveles: carpeta/subcarpetas/archivos)
    def obtenerExpedientes(self):
        """
        - Obtiene la ruta seleccionada por el usuario,
        - Recupera la lista de carpetas en esa ruta
        """

        folder_selected = os.path.normpath(filedialog.askdirectory())
        # Valida si no selecciona carpeta y muestra la carpeta seleccionada en el widget de texto
        if folder_selected == "." or folder_selected == "":  # Si no se selecciona ninguna carpeta
            tk.messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carpeta.")
        else:
            # print("Carpeta seleccionada: ", folder_selected)
            self.expediente = folder_selected
            self.text_widget.insert(tk.END, "Carpeta seleccionada: " + folder_selected + "\n")
            self.text_widget.see(tk.END)

            # Obtener la lista de carpetas en la carpeta seleccionada
            carpetas = [os.path.join(folder_selected, d) for d in os.listdir(folder_selected) if os.path.isdir(os.path.join(folder_selected, d))]
            self.carpetas = carpetas

    def procesaCarpetas(self):
        """
        - Crea objeto y llama metodo process() para cada carpeta en la lista
        """
        total_carpetas = len(self.carpetas)
        self.progress["maximum"] = 1  # La barra de progreso va de 0 a 1

        if self.carpetas != []:	
            num_carpetas = len(self.carpetas)
            if tk.messagebox.askyesno(
                    message=f'Se procesarán {num_carpetas} carpetas que contiene la carpeta "{os.path.basename(self.expediente)}". \n¿Desea continuar?.',
                    title=os.path.basename(self.expediente),
                ):
                # Indicar al usuario que el proceso ha comenzado
                self.progress["value"] = 0.1
                self.text_widget.insert(tk.END, "Proceso iniciado...\n")
                # self.text_widget.insert(tk.END, "CARPETAS PROCESADAS:\n")
                self.update_idletasks()

                for i, carpeta in enumerate(self.carpetas):
                    despacho = self.entry01.get()
                    subserie = self.entry02.get()

                    # Obtener el valor de entry03
                    rdo = self.entry03.get().strip()

                    # Si entry03 está vacío, usar el nombre de la carpeta como rdo
                    if rdo == "":
                        rdo = os.path.basename(carpeta)

                    print("RDO: ", rdo)
                    self.text_widget.insert(tk.END, subserie+"/"+rdo+"\n")
                    self.text_widget.see(tk.END)

                    obj = AutomatizacionEmpleado(carpeta, "", despacho, subserie, rdo)
                    obj.process()

                    # Actualizar la barra de progreso
                    self.progress["value"] = 0.1 + ((i + 1) / total_carpetas) * 0.9
                    self.update_idletasks()

                # Indicar al usuario que el proceso ha terminado
                self.progress["value"] = 1.0  # Asegurarse de que la barra de progreso llegue al 100%
                self.update_idletasks()
                self.expediente = ""
                self.carpetas = []
                self.text_widget.insert(tk.END, "Proceso completado.\n")
                self.update_idletasks()
                self.mensaje(1)
            else:
                self.expediente = ""
                self.carpetas = []
                self.mensaje(6)
        else:
            self.mensaje(3)

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
                self.expediente = ""
                self.carpetas = []
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
            self.text_widget.insert(tk.END, "\n")
            # self.text_widget.insert(tk.END, switcher.get(result))
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
        else:
            """ self.entry1.config(state=tk.NORMAL)
            self.entry1.delete(0, tk.END)
            self.entry1.insert(0, items)
            self.entry1.config(state=tk.DISABLED) """

    def obtener_version_actual(self):
        # Determinar la ruta del archivo xlsm
        if getattr(sys, 'frozen', False):
            # Si se está ejecutando el archivo empaquetado
            bundle_dir = sys._MEIPASS
        else:
            # Si se está ejecutando desde el script original
            bundle_dir = os.path.abspath(os.path.dirname(__file__))

        ruta_json = os.path.join(bundle_dir, 'assets/last_version.json')
        with open(ruta_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            version = data.get('version')
        return version

    def comprobar_actualizaciones(self):
        url = "https://raw.githubusercontent.com/HammerDev99/GestionExpedienteElectronico_Version1/refs/heads/master/assets/last_version.json"  # O usa la URL de raw.githubusercontent.com
        try:
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            version_actual = list(map(int, self.obtener_version_actual().split(".")))
            ultima_version = list(map(int, datos.get('version').split(".")))

            if version_actual < ultima_version:
                # Actualizar variable para mostrar notificación en un label de la GUI
                return False # la variable is_updated se actualiza a False
            else:
                return True # la variable is_updated se mantiene en True
        except requests.RequestException as e:
            print(f"Error al comprobar actualizaciones: {e}")

root = tk.Tk()
app = Application(root)
app.mainloop()
