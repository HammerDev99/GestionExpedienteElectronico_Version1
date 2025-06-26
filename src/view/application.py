# coding=utf-8

from tkinter import filedialog
from tkinter import ttk
import asyncio
import csv
import json
import logging
import os.path
import requests
import send2trash
import sys
import tkinter as tk
import webbrowser

# Detectar entorno y configurar importaciones
if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.utils.resource_manager import resource_manager
    from src.view.tooltip import Tooltip
    from src.view.tools_launcher import ToolsLauncher
    from src.model.file_processor import FileProcessor
    from src.model.folder_analyzer import FolderAnalyzer
    from src.controller.processing_context import ProcessingContext
    from src.controller.gui_notifier import (
        GUINotifier,
        TextWidgetObserver,
        ProgressBarObserver,
        DialogObserver,
        StatusLabelObserver,
    )
else:
    # Entorno de desarrollo
    from utils.resource_manager import resource_manager
    from view.tooltip import Tooltip
    from view.tools_launcher import ToolsLauncher
    from model.file_processor import FileProcessor
    from model.folder_analyzer import FolderAnalyzer
    from controller.processing_context import ProcessingContext
    from controller.gui_notifier import (
        GUINotifier,
        TextWidgetObserver,
        ProgressBarObserver,
        DialogObserver,
        StatusLabelObserver,
    )


class Application(ttk.Frame):

    expediente = ""
    carpetas = []
    is_updated = True
    selected_value = "2"
    lista_subcarpetas = []
    analyzer = None
    profundidad = None
    carpetas_omitidas = list()
    processor = None

    def __init__(self, root, logger=None):
        """
        @param: root tipo Tk; contiene la raíz de la aplicación Tkinter
        @modules: tkinter
        - Inicializa la aplicación, configura la ventana principal y crea los widgets.
        """

        self.root = root
        self.logger = logger or logging.getLogger("GUI")
        self.logger.info("Iniciando interfaz gráfica")
        self.profundidad = None
        try:
            super().__init__(root)
            root.title("AgilEx by Marduk " + self._obtener_version_actual())
            root.resizable(False, False)
            # root.geometry("350x300")
            root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.pack(padx=20, pady=20)  # Añadir padding aquí

            # Configurar el sistema de notificación
            self.gui_notifier = GUINotifier()
            self.create_oneProcessWidgets()

            # Crear y registrar observadores
            text_observer = TextWidgetObserver(self.text_widget)
            progress_observer = ProgressBarObserver(self.progress)
            dialog_observer = DialogObserver(root)
            status_label_observer = StatusLabelObserver(self.status_var)

            # Registrar observadores para tipos específicos
            self.gui_notifier.attach(text_observer)
            self.gui_notifier.attach(progress_observer)
            self.gui_notifier.attach(dialog_observer)
            self.gui_notifier.attach(status_label_observer)

            # Crear ProcessingContext con el notificador y el logger
            self.processing_context = ProcessingContext(self.gui_notifier, self.logger)
            
            # Programa el mensaje después de la inicialización
            self.root.after(300, self.initial_message)
        except Exception as e:
            self.logger.error(f"Error en inicialización GUI: {str(e)}", exc_info=True)
            raise

    def create_oneProcessWidgets(self):
        """
        @modules: tkinter
        - Crea y configura los widgets de la interfaz gráfica.
        """
        self.is_updated = (
            self._comprobar_actualizaciones()
        )  # Comprobar actualizaciones al iniciar la aplicación

        # Crear barra de menú
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # Crear menú de ayuda
        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Ayuda", menu=self.help_menu)
        self.help_menu.add_command(
            label="📋 Guía Rápida del Programa", command=self.mostrar_guia_rapida
        )
        self.help_menu.add_separator()
        self.help_menu.add_command(
            label="Banco de Herramientas Complementarias", command=self.open_tools_window, state="normal"
        )
        self.help_menu.add_separator()
        self.help_menu.add_command(
            label="Video tutorial (link 1)",
            command=lambda: self._callback("https://enki.care/Ultimate"),
        )
        self.help_menu.add_command(
            label="Video tutorial (link 2)",
            command=lambda: self._callback("https://enki.care/UltimateY"),
        )
        self.help_menu.add_separator()
        self.help_menu.add_command(
            label="Experto en expediente electrónico (agente IA)",
            command=lambda: self._callback(
                "https://enki.care/Experto_en_Expediente_Electronico"
            ),
        )
        self.help_menu.add_separator()
        self.help_menu.add_command(
            label="Tablas de retención documental",
            command=lambda: self._callback(
                "https://enki.care/Tablas_Retencion_Documental"
            ),
        )
        self.help_menu.add_command(
            label="Protocolo de gestión de expedientes electrónicos v2",
            command=lambda: self._callback(
                "https://enki.care/Protocolo_Gestion_Expedientes_Electrónicos_v2"
            ),
        )
        self.help_menu.add_command(
            label="Condiciones archivísticas mínimas para migrar a Alfresco",
            command=lambda: self._callback(
                "https://enki.care/Condiciones_Archivisticas_Minimas_Alfresco"
            ),
        )

        self.label_frame = tk.Frame(self)
        self.label_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Definir una constante para el literal "<Button-1>"
        BUTTON_CLICK_EVENT = "<Button-1>"

        self.label1 = tk.Label(
            self.label_frame, text="Daniel Arbelaez Alvarez", fg="blue", cursor="hand2"
        )
        self.label1.pack(side=tk.LEFT)
        self.label1.bind(
            BUTTON_CLICK_EVENT,
            lambda e: self._callback("https://www.linkedin.com/in/daniel-arbelaez-/"),
        )

        self.label2 = tk.Label(
            self.label_frame, text="| HammerDev99", fg="blue", cursor="hand2"
        )
        self.label2.pack(side=tk.LEFT)
        self.label2.bind(
            BUTTON_CLICK_EVENT,
            lambda e: self._callback("https://github.com/HammerDev99"),
        )

        if not self.is_updated:
            # Crear un contenedor para el label de actualización
            self.update_frame = tk.Frame(self)
            self.update_frame.pack(side=tk.TOP, fill=tk.X)

            self.update_label = tk.Label(
                self.update_frame,
                text="🚀 Nueva versión disponible",
                fg="green",
                cursor="hand2",
            )
            self.update_label.pack(side=tk.RIGHT, padx=0, pady=0)
            self.update_label.bind(
                "<Button-1>",
                lambda e: self._callback(
                    "https://enki.care/Latest_Agilex_By_Marduk"
                ),
            )

        # Crear un Frame para contener el label01 y el icono de ayuda
        self.frame_label01 = tk.Frame(self)
        self.frame_label01.pack(pady=5, anchor="center")

        # Crear icono de ayuda
        self.icono_ayuda = tk.Label(
            self.frame_label01,
            text="ℹ️",
            font=("Helvetica", 12),
            fg="blue",
            cursor="hand2",
        )
        self.icono_ayuda.pack(side=tk.LEFT, padx=(5, 0))

        self.label01 = tk.Label(
            self.frame_label01, text="Despacho Judicial:", font=("Helvetica", 12)
        )
        self.label01.pack(side=tk.LEFT)

        # Añadir tooltip al icono de ayuda
        Tooltip(
            self.icono_ayuda,
            image_path=None,
            text="Ingrese el nombre exacto del Despacho Judicial según el sistema validador/migrador",
        )

        # Crear el Combobox para entry01
        self.entry01 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry01.pack(pady=5)

        # Crear un Frame para contener el label01 y el icono de ayuda
        self.frame_label02 = tk.Frame(self)
        self.frame_label02.pack(pady=5, anchor="center")

        # Crear icono de ayuda
        self.icono_ayuda = tk.Label(
            self.frame_label02,
            text="ℹ️",
            font=("Helvetica", 12),
            fg="blue",
            cursor="hand2",
        )
        self.icono_ayuda.pack(side=tk.LEFT, padx=(5, 0))

        self.label02 = tk.Label(
            self.frame_label02, text="Serie o Subserie:", font=("Helvetica", 12)
        )
        self.label02.pack(side=tk.LEFT)

        # Añadir tooltip al icono de ayuda
        Tooltip(
            self.icono_ayuda,
            image_path=None,
            text="Ingrese el nombre exacto de la serie documental según el sistema validador/migrador o la TRD",
        )

        # Crear el Combobox para entry02
        self.entry02 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry02.pack(pady=5)

        self.load_csv_values(self.entry01, resource_manager.get_path("src/assets/JUZGADOS.csv")) # funciona en producción
        self.load_csv_values(self.entry02, resource_manager.get_path("src/assets/TRD.csv")) # funciona en producción

        # Crea un Frame para el label de tipo de gestión
        self.frame_label_tipo_gestion = tk.Frame(self)
        self.frame_label_tipo_gestion.pack(pady=5, anchor="center")

        # Crear icono de ayuda
        self.icono_ayuda = tk.Label(
            self.frame_label_tipo_gestion,
            text="ℹ️",
            font=("Helvetica", 12),
            fg="blue",
            cursor="hand2",
        )
        self.icono_ayuda.pack(side=tk.LEFT, padx=(5, 0))

        self.label_tipo_gestion = tk.Label(
            self.frame_label_tipo_gestion, text="Tipo de Gestión:", font=("Helvetica", 12)
        )
        self.label_tipo_gestion.pack(side=tk.LEFT)

        # Añadir tooltip al icono de ayuda
        Tooltip(
            self.icono_ayuda,
            image_path=None,
            text="Cuaderno: Sólo el cuaderno de un expediente\nExpediente: Todos los cuadernos del expediente de un solo proceso.\nMúltiples Expedientes: varios expedientes de procesos de una misma serie o subserie",
        )

        # Crear un Frame para los Radiobuttons
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=5)

        # Variable para los Radiobuttons
        self.radio_var = tk.StringVar(value="2")
        self.radio_var.trace("w", self._on_radio_change)

        # Crear los Radiobuttons
        self.radio1 = ttk.Radiobutton(
            self.radio_frame,
            text="Cuaderno", #: Selecciona\nun solo cuaderno",
            variable=self.radio_var,
            value="1"
        )
        self.radio1.pack(side=tk.LEFT, padx=10)
        self.radio2 = ttk.Radiobutton(
            self.radio_frame,
            text="Expediente", #: Selecciona la\ncarpeta de un proceso",
            variable=self.radio_var,
            value="2"
        )
        self.radio2.pack(side=tk.LEFT, padx=10)
        self.radio3 = ttk.Radiobutton(
            self.radio_frame,
            text="Múltiples Expedientes", #: Selecciona la \ncarpeta de la subserie",
            variable=self.radio_var,
            value="3"
        )
        self.radio3.pack(side=tk.LEFT, padx=10)

        # Crear el frame para label03 y entry03 desde el inicio
        self.frame_label03 = tk.Frame(self)
        self.frame_label03.pack(pady=5, padx=5, anchor="center")
        
        self.label03 = tk.Label(
            self.frame_label03, text="Radicado", font=("Helvetica", 12), padx=5
        )
        self.label03.pack(side=tk.LEFT)
        
        self.entry03 = tk.Entry(self.frame_label03, width=75, justify="center")
        self.entry03.pack(pady=5)
        
        # Inicialmente deshabilitar el entry si no es la opción 1
        if self.radio_var.get() != "1":
            self.entry03.configure(state="disabled")

        # Crear tooltips con imágenes para los Radiobuttons
        self._create_tooltips()

        # Crear una barra de desplazamiento vertical
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Crear un Text widget para mostrar los procesos realizados
        self.text_widget = tk.Text(
            self, width=50, height=20, yscrollcommand=self.scrollbar.set
        )
        self.text_widget.configure(wrap="word") # Configurar el modo de ajuste
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # Configurar la barra de desplazamiento para el Text widget
        self.scrollbar.config(command=self.text_widget.yview)

        self.pathExpediente = tk.Button(
            self,
            text="Agregar carpeta",
            command=self.obtener_rutas,
            height=1,
            width=17,
        )
        self.pathExpediente.pack(side=tk.LEFT, padx=5)

        # Crear un Frame para contener la barra de progreso y el Label de estado
        self.progress_frame = tk.Frame(self)
        self.progress_frame.pack(side=tk.LEFT, padx=5, pady=5)

        # Barra de progreso
        self.progress = ttk.Progressbar(
            self.progress_frame, orient="horizontal", length=300, mode="determinate"
        )
        self.progress.pack(fill=tk.BOTH, expand=True)

        # Variable de control para el estado
        self.status_var = tk.StringVar(value="")

        # Label de estado superpuesto a la barra de progreso
        self.status_label = ttk.Label(
            self.progress_frame,  # Usar el mismo contenedor que la barra de progreso
            textvariable=self.status_var,
            font=("Helvetica", 9),
            background="",  # Fondo transparente
        )
        self.status_label.place(
            relx=0.5, rely=0.5, anchor="center"
        )  # Centrar el Label sobre la barra de progreso

        # Botón Aceptar
        self.aceptar = tk.Button(
            self,
            text="Aceptar",
            command=lambda: self.run_async_process(self),
            height=1,
            width=10,
        )
        self.aceptar.pack(side=tk.LEFT, padx=5)

        # Otros widgets...
        self.label5 = tk.Label(self, text="")
        self.label5.pack(side=tk.LEFT)
        #self.initial_message()
        self.pack()

    def open_tools_window(self):
        """Abre la ventana del banco de herramientas"""
        try:
            ToolsLauncher(self.root, logger=self.logger)
        except Exception as e:
            self.logger.error(f"Error al abrir el banco de herramientas: {str(e)}", exc_info=True)
            tk.messagebox.showerror(
                "Error", 
                f"No se pudo abrir el banco de herramientas:\n{str(e)}"
            )

    def _restablecer_variables_clase(self):
        """
        Restablece las variables de la clase a su estado inicial.
        """
        self.expediente = ""
        self.carpetas = []
        self.lista_subcarpetas = []
        self.analyzer = None
        self.profundidad = None
        self.carpetas_omitidas = list()

        self.lista_cui = []
        self.estructura_directorios = {}
    
    def initial_message(self):
        initial_message = (
            "1. Ingrese los datos de 'Despacho Judicial' y 'Serie o Subserie'\n\n"
            "2. Seleccione una el 'Tipo de Gestión' según su necesidad\n\n"
            "3. Agregue la carpeta a procesar\n\n"
            "4. Presione Aceptar para iniciar\n\n"
        )
        tk.messagebox.showinfo("Guía rápida", initial_message)

    def update_progressbar_status(self, message):
        """Actualiza el mensaje de estado."""
        self.status_var.set(message)

    def mostrar_guia_rapida(self):
        # Crear una ventana emergente
        guia_rapida_window = tk.Toplevel(self.root)
        guia_rapida_window.title("Guía Rápida del Programa")
        guia_rapida_window.geometry("600x400")
        guia_rapida_window.resizable(False, False)

        # Crear un Text widget para mostrar el mensaje de la guía rápida
        text_widget = tk.Text(guia_rapida_window, wrap="word", padx=10, pady=10)
        text_widget.pack(expand=True, fill="both")

        # Mensaje de la guía rápida
        mensaje_guia_rapida = (
            "📋 Guía Rápida del Programa\n\n"
            "1. Datos del SGDE\n\n"
            "• Use exactamente los mismos datos de 'Despacho Judicial' y 'Serie o Subserie' registrados en migrador/validador y/o la TRD\n\n"
            "2. Preparación de Carpetas\n\n"
            "• Nombres de archivos: Organizados mínimo secuencialmente\n"
            "• Radicado: Debe contener 23 dígitos\n\n"
            "3. Estructura de Carpetas\n\n"
            "🔹 Cuaderno:\n"
            "   C01Principal/Archivos\n\n"
            "🔹 Proceso:\n"
            "   RADICADO/01PrimeraInstancia/C01Principal/Archivos\n\n"
            "🔹 Subserie:\n"
            "   SERIE_SUBSERIE/RADICADO/01PrimeraInstancia/C01Principal/Archivos\n\n"
        )

        # Insertar el mensaje en el Text widget
        text_widget.insert(tk.END, mensaje_guia_rapida)
        text_widget.config(
            state=tk.DISABLED
        )  # Hacer que el Text widget sea de solo lectura

    def _on_radio_change(self, *args):
        self.selected_value = self.radio_var.get()
        self.logger.info(f"Opción seleccionada: {self.selected_value}")

        # En lugar de ocultar/mostrar, habilitar/deshabilitar
        if self.selected_value == "1":
            self.entry03.delete(0, tk.END)
            self.entry03.configure(state="normal")
        else:
            self.entry03.delete(0, tk.END)
            self.entry03.configure(state="disabled")
            
        self.progress['maximum'] = 1
        self.progress["value"] = 0
        self.entry03.delete(0, tk.END)
        self.update_progressbar_status("")

    def _create_tooltips(self):
        """
        Crea tooltips para los radiobuttons usando imágenes.
        """
        image_paths = [
            resource_manager.get_path("src/assets/tooltip1.png"),
            resource_manager.get_path("src/assets/tooltip2.png"),
            resource_manager.get_path("src/assets/tooltip3.png")
        ]

        # Tooltip(self.radio1, image_paths[0])  # Comentado
        Tooltip(self.radio1, image_paths[0], text=None)
        Tooltip(self.radio2, image_paths[1], text=None)
        Tooltip(self.radio3, image_paths[2], text=None)

    def _callback(self, url):
        """
        @modules: webbrowser
        """
        webbrowser.open_new(url)

    def _on_closing(self):
        """
        @modules: tkinter

        Maneja el evento de cierre de la ventana.
        Se llama tanto para la X como para el botón Cancelar.
        """
        self.logger.info("Iniciando proceso de cierre de aplicación")
        try:
            # Preguntar si realmente quiere cerrar
            if tk.messagebox.askokcancel(
                "Confirmar cierre", "¿Está seguro que desea cerrar la aplicación?"
            ):

                self.logger.info("Usuario confirmó cierre de aplicación")

                # Limpiar recursos
                # self._cleanup()

                # Cerrar ventana principal y terminar aplicación
                self.root.quit()
                self.root.destroy()
                self.logger.info("Aplicación cerrada correctamente")
            else:
                self.logger.info("Usuario canceló cierre de aplicación")

        except Exception as e:
            self.logger.error(f"Error al cerrar la aplicación: {str(e)}", exc_info=True)
            # Forzar cierre en caso de error
            self.root.destroy()

    def load_csv_values(self, entry: ttk.Combobox, ruta: str):
        """
        Carga los valores del archivo CSV en el combobox.
        """
        csv_file_path = ruta
        values = []

        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                values.append(row["nombre"].upper())

        entry["values"] = values
        if values:
            entry.set(values[0])

    def _cleanup(self):
        """
        Limpia recursos antes de cerrar.
        """
        try:
            self.logger.debug("Iniciando limpieza de recursos")

            # Cerrar procesos de Excel si existen
            if hasattr(self, "analyzer") and self.analyzer:
                self.logger.debug("Cerrando procesos de Excel")
                # Implementar cierre de procesos Excel

            # Limpiar archivos temporales
            temp_files = ["temp_process_data.json", "temp_excel_script.py"]
            for file in temp_files:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        self.logger.debug(f"Archivo temporal eliminado: {file}")
                    except Exception as e:
                        self.logger.warning(
                            f"No se pudo eliminar archivo temporal {file}: {str(e)}"
                        )

            # Restablecer variables
            self._restablecer_variables_clase()
            self.update_progressbar_status("")
            self.logger.debug("Limpieza de recursos completada")

        except Exception as e:
            self.logger.error(f"Error en limpieza de recursos: {str(e)}", exc_info=True)

    def _obtener_version_actual(self):
        # Determinar la versión del programa
        ruta_json = resource_manager.get_path("src/assets/last_version.json") 
        with open(ruta_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            version = data.get("version")
        return version

    def _comprobar_actualizaciones(self):
        url = "https://raw.githubusercontent.com/HammerDev99/GestionExpedienteElectronico_Version1/refs/heads/master/src/assets/last_version.json"  # O usa la URL de raw.githubusercontent.com
        try:
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            version_actual = list(map(int, self._obtener_version_actual().split(".")))
            ultima_version = list(map(int, datos.get("version").split(".")))

            if version_actual < ultima_version:
                # Actualizar variable para mostrar notificación en un label de la GUI
                return False  # la variable is_updated se actualiza a False
            else:
                return True  # la variable is_updated se mantiene en True
        except requests.RequestException as e:
            self.logger.error(f"Error al comprobar actualizaciones: {e}", exc_info=True)

    # Pendiente refactorizar para implementar el patrón strategy con opción subcarpeta, opción 1 y opción 2
    def obtener_rutas(self):
        """
        - Obtiene la ruta seleccionada por el usuario
        - Recupera la lista de carpetas en esa ruta
        - Valida la estructura de las carpetas
        - Obtiene los CUIs y subcarpetas internas
        """
        self.text_widget.see(tk.END)
        self.lista_cui = []
        self.lista_subcarpetas = []
        self.carpetas_omitidas = set()
        self.estructura_directorios = {}

        #**********************************
        folder_selected = os.path.normpath(filedialog.askdirectory())
        if folder_selected in [".", ""]:
            tk.messagebox.showwarning(
                "Advertencia", "No se ha seleccionado ninguna carpeta."
            )
            return
        self.text_widget.insert(tk.END, "\n*******************")

        # **********************************
        # Implementación del patron strategy opción subcarpetas
        # Agrega la carpeta seleccionada utilizando el contexto para el caso de la opcion subcarpetas
        if self.selected_value == "1":

            # Procesar archivo
            despacho = self.entry01.get()
            subserie = self.entry02.get()
            radicado = self.entry03.get()

            # validar que existan archivos en la carpeta seleccionada
            estructura_directorios = os.listdir(folder_selected)
            if not estructura_directorios:
                tk.messagebox.showwarning(
                    "Advertencia",
                    "La carpeta seleccionada está vacía o no es accesible.",
                )
                return
            # Validar con el usuario a través de un mensaje de confirmación solo en el caso en que dentro de la carpeta seleccionada existan más carpetas adentro
            #********************************** Funcion repetida integrar en varias funciones adicionales
            carpetas = []
            for carpeta in estructura_directorios:
                if os.path.isdir(os.path.join(folder_selected, carpeta)):
                    carpetas.append(carpeta)
            cadena_rutas_anexos = ""
            for i in carpetas:
                cadena_rutas_anexos += "   🔹"+i + "\n"
            if len(carpetas) > 1:
                self.text_widget.insert(tk.END, f"\n-------------------\n❕ Se encontraron anexos masivos en:\n\n{cadena_rutas_anexos}")
                self.text_widget.see(tk.END)
            #**********************************

            processor = FileProcessor(
                folder_selected, "", despacho, subserie, radicado, logger=self.logger
            )
            self.processor = processor
            self.processing_context.add_folder(self.selected_value, processor)

            return
        # **********************************

        # Crear una instancia del analizador de carpetas
        analyzer = FolderAnalyzer({}, None, logger=self.logger)

        self.expediente = folder_selected
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            tk.messagebox.showwarning(
                "Advertencia", "La carpeta seleccionada está vacía o no es accesible."
            )
            return

        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        # Para poder incorporarla generación de lista de rutas donde se encuentran archivos sueltos donde Solo deberían de ir carpetas se pretende estructurar el objeto folder analizer enviando igualmente el valor seleccionado para que inmediatamente si haga el análisis se genere las rutas de esas carpetas y se vuelva en una variable
        analyzer = FolderAnalyzer(
            estructura_directorios, profundidad_maxima, logger=self.logger
        )

        # **********************************
        # Implementación del patron strategy para opciones Expediente y Múltiples Expedientes
        # Agregar la carpeta seleccionada utilizando el contexto para selected_value "2" y "3"
        if self.selected_value in ["2", "3"]:
            # Obtener datos del formulario
            despacho = self.entry01.get()
            subserie = self.entry02.get()
            
            # Para las estrategias 2 y 3, no necesitamos FileProcessor en add_folder
            # Pasar la carpeta ya seleccionada para evitar duplicación
            result = self.processing_context.add_folder(self.selected_value, None, despacho, subserie, folder_selected)
            
            # Si la estrategia retorna datos, configurar las variables de clase
            if result and isinstance(result, dict):
                self.expediente = result.get('expediente')
                self.lista_subcarpetas = result.get('lista_subcarpetas', [])
                self.carpetas_omitidas = result.get('carpetas_omitidas', set())
                self.analyzer = result.get('analyzer')
                self.profundidad = result.get('profundidad')
                
                # Actualizar la barra de progreso según el resultado
                if not self.lista_subcarpetas:
                    self.update_progressbar_status("")
                else:
                    self.progress['maximum'] = 1
                    self.progress["value"] = 1
                    self.update_progressbar_status("Listo para procesar")
            
            return
        # **********************************













    def run_async_process(self, app):
        """Inicia el procesamiento asíncrono"""
        asyncio.run(app.procesa_expedientes())

    # Pendiente refactorizar para implementar el patrón strategy con opción subcarpeta, opción 1 y opción 2
    async def procesa_expedientes(self):
        """Versión asíncrona simplificada del procesamiento de expedientes"""
        despacho = self.entry01.get()
        subserie = self.entry02.get()

        if not self.lista_subcarpetas and (
            self.selected_value != "1" or self.processor is None
        ):
            self._mensaje(3)
            return

        self.logger.info(f"Procesando {len(self.lista_subcarpetas)} expedientes")
        total_carpetas = sum(len(sublista) for sublista in self.lista_subcarpetas)
        self.progress["maximum"] = 1  # La barra de progreso va de 0 a 1

        # Se realiza conteo de archivos lo cual debería de estar en la estrategia pero por el momento se realiza en este punto
        # Solo mostrar confirmación para selected_value == "1", las estrategias manejan su propia confirmación
        if self.selected_value == "1":
            total_archivos = len(os.listdir(self.processor.get_ruta()))
            
            if not tk.messagebox.askyesno(
                message=f'Se procesarán {total_archivos} archivos que contiene la carpeta '
                f'"{os.path.basename(self.processor.get_ruta())}". '
                f"¿Desea continuar?.",
                title=os.path.basename(self.processor.get_ruta()),
            ):
                self._restablecer_variables_clase()
                self.update_progressbar_status("")
                self._mensaje(6)
                return

        # **********************************
        # Implementación del patron strategy opción subcarpetas
        # Procesa la carpeta seleccionada utilizando el contexto para el caso de la opcion subcarpetas
        if self.selected_value == "1":
            processor = FileProcessor(
                self.processor.get_ruta(),
                "",
                despacho,
                subserie,
                self.entry03.get(),
                logger=self.logger,
            )
            await self.processing_context.process_folder(self.selected_value, self.processor)
            self.processor = None
            self._restablecer_variables_clase()
            return
        # **********************************

        # **********************************
        # Implementación del patron strategy para opciones Expediente y Múltiples Expedientes
        # Procesa la carpeta seleccionada utilizando el contexto para selected_value "2" y "3"
        elif self.selected_value in ["2", "3"]:
            # Para las estrategias 2 y 3, necesitamos acceso a la estrategia para usar sus datos internos
            strategy = self.processing_context._strategies.get(self.selected_value)
            
            if not strategy or not hasattr(strategy, 'expediente') or not strategy.expediente:
                self._mensaje(3)  # "Seleccione una carpeta para procesar"
                return
            
            # Crear un FileProcessor con los datos del formulario y la información de la estrategia
            processor = FileProcessor(
                strategy.expediente,  # Usar la ruta configurada en add_folder()
                "",
                despacho,
                subserie,
                "",  # El RDO se maneja internamente por las estrategias
                logger=self.logger,
            )
            
            # Usar el contexto para procesar según la estrategia correspondiente
            await self.processing_context.process_folder(self.selected_value, processor)
            
            # Limpiar variables después del procesamiento
            self._restablecer_variables_clase()
            return
        # **********************************

    def _mensaje(self, result=None, mensaje=None):
        """
        @param: result tipo int
        @modules: tkinter
        - Utiliza la GUI para enviar mensaje
        """
        switcher = {
            0: "Procedimiento detenido. No se encontraron los archivos indicados en el índice",
            1: "Proceso completado exitosamente",
            2: "Archivos sin procesar",
            3: "Seleccione una carpeta para procesar",
            6: "Procedimiento detenido",
        }
        if result != None:
            tk.messagebox.showinfo(
                message=switcher.get(result), title=os.path.basename(self.expediente)
            )
            self.text_widget.insert(tk.END, "\n")
            self.text_widget.see(tk.END)
            self.logger.info(switcher.get(result), exc_info=True)

        if mensaje != None:
            tk.messagebox.showinfo(
                message=mensaje, title=os.path.basename(self.expediente)
            )
            self.logger.info(switcher.get(result), exc_info=True)

    def _get_bundled_path(self, ruta):
        """
        Obtiene la ruta correcta según el entorno de ejecución.

        Args:
            ruta (str): Ruta relativa al directorio base

        Returns:
            str: Ruta absoluta normalizada
        """
        return resource_manager.get_path(ruta)
