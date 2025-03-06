# coding=utf-8

import select
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import os.path
import sys
import webbrowser
import requests
import json
from file_processor import FileProcessor
from folder_analyzer import FolderAnalyzer
from tooltip import Tooltip
import logging
import asyncio
import csv
import send2trash
from processing_context import ProcessingContext
from gui_notifier import (
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
        except Exception as e:
            self.logger.error(f"Error en inicialización GUI: {str(e)}", exc_info=True)
            raise

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
                "https://www.ramajudicial.gov.co/web/centro-de-documentacion-judicial/tablas-de-retencion-documental"
            ),
        )
        self.help_menu.add_command(
            label="Protocolo de gestión de expedientes electrónicos v2",
            command=lambda: self._callback(
                "https://www.ramajudicial.gov.co/documents/3196516/46103054/Protocolo+para+la+gesti%C3%B3n+de+documentos+electronicos.pdf/cb0d98ef-2844-4570-b12a-5907d76bc1a3"
            ),
        )
        self.help_menu.add_command(
            label="Condiciones archivísticas mínimas para migrar a Alfresco",
            command=lambda: self._callback(
                "https://etbcsj-my.sharepoint.com/:b:/g/personal/darbelaal_cendoj_ramajudicial_gov_co/EarfmwGQYoFEtXQRCsVmPIABMoZI4TRuIEq58mnOC0-Qyw?e=v6Tk1m"
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
                    "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/latest"
                ),
            )

        # Crear un Frame para contener el label01 y el icono de ayuda
        self.frame_label01 = tk.Frame(self)
        self.frame_label01.pack(pady=5, anchor="center")

        self.label01 = tk.Label(
            self.frame_label01, text="Juzgado", font=("Helvetica", 12)
        )
        self.label01.pack(side=tk.LEFT)

        # Crear icono de ayuda
        self.icono_ayuda = tk.Label(
            self.frame_label01,
            text="ℹ️",
            font=("Helvetica", 12),
            fg="blue",
            cursor="hand2",
        )
        self.icono_ayuda.pack(side=tk.LEFT, padx=(5, 0))

        # Añadir tooltip al icono de ayuda
        Tooltip(
            self.icono_ayuda,
            image_path=None,
            text="Ingrese el nombre exacto del juzgado según el sistema validador/migrador",
        )

        # Crear el Combobox para entry01
        self.entry01 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry01.pack(pady=5)

        # Leer el archivo CSV y obtener los valores para el Combobox
        self.load_csv_values(self.entry01, "assets/JUZGADOS.csv")

        # Crear un Frame para contener el label01 y el icono de ayuda
        self.frame_label02 = tk.Frame(self)
        self.frame_label02.pack(pady=5, anchor="center")

        self.label02 = tk.Label(
            self.frame_label02, text="Serie o Subserie", font=("Helvetica", 12)
        )
        self.label02.pack(side=tk.LEFT)

        # Crear icono de ayuda
        self.icono_ayuda = tk.Label(
            self.frame_label02,
            text="ℹ️",
            font=("Helvetica", 12),
            fg="blue",
            cursor="hand2",
        )
        self.icono_ayuda.pack(side=tk.LEFT, padx=(5, 0))

        # Añadir tooltip al icono de ayuda
        Tooltip(
            self.icono_ayuda,
            image_path=None,
            text="Ingrese el nombre exacto de la serie documental según el sistema validador/migrador o la TRD",
        )

        # Crear el Combobox para entry02
        self.entry02 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry02.pack(pady=5)

        # Leer el archivo CSV y obtener los valores para el Combobox
        self.load_csv_values(self.entry02, "assets/TRD.csv")

        # Crear un Frame para contener el label03 y el icono de ayuda
        self.frame_label03 = tk.Frame(self)
        self.frame_label03.pack(pady=5, padx=5, anchor="center")

        self.label03 = tk.Label(
            self.frame_label03, text="Radicado", font=("Helvetica", 12), padx=5
        )

        self.entry03 = tk.Entry(self.frame_label03, width=25, justify="center")

        # Crear un Frame para los Radiobuttons
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=5)

        # Variable para los Radiobuttons
        self.radio_var = tk.StringVar(value="2")
        self.radio_var.trace("w", self._on_radio_change)

        # Crear los Radiobuttons
        self.radio1 = ttk.Radiobutton(
            self.radio_frame,
            text="Cuaderno: Selecciona\nun solo cuaderno",
            variable=self.radio_var,
            value="1",
        )
        self.radio1.pack(side=tk.LEFT, padx=10)
        self.radio2 = ttk.Radiobutton(
            self.radio_frame,
            text="Proceso: Selecciona la\ncarpeta de un proceso",
            variable=self.radio_var,
            value="2",
        )
        self.radio2.pack(side=tk.LEFT, padx=10)
        self.radio3 = ttk.Radiobutton(
            self.radio_frame,
            text="Subserie: Selecciona la \ncarpeta de la subserie",
            variable=self.radio_var,
            value="3",
        )
        self.radio3.pack(side=tk.LEFT, padx=10)

        # Crear tooltips con imágenes para los Radiobuttons
        self._create_tooltips()

        # Crear una barra de desplazamiento vertical
        self.scrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)

        # Crear un Text widget para mostrar los RDOs procesados
        self.text_widget = tk.Text(
            self, width=50, height=20, yscrollcommand=self.scrollbar.set
        )
        self.text_widget.pack(fill="both", expand=True, padx=5, pady=5)

        # Mensaje inicial en el text widget
        initial_message = (
            "\n   Pasos:\n"
            "   1. Ingrese los datos de Juzgado y Serie/Subserie\n"
            "   2. Seleccione una opción según su necesidad\n"
            "   3. Agregue la carpeta a procesar\n"
            "   4. Presione Aceptar para iniciar\n"
        )
        self.text_widget.insert(tk.END, initial_message)

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
            width=7,
        )
        self.aceptar.pack(side=tk.LEFT, padx=5)

        # Botón Cancelar
        self.cancelar = tk.Button(
            self, text="Cancelar", fg="red", command=self._on_closing, height=1, width=7
        )
        self.cancelar.pack(side=tk.LEFT, padx=5)

        # Otros widgets...
        self.label5 = tk.Label(self, text="")
        self.label5.pack(side=tk.LEFT)

        self.pack()

    def update_progressbar_status(self, message):
        """Actualiza el mensaje de estado."""
        self.status_var.set(message)

    def mostrar_guia_rapida(self):
        # Crear una ventana emergente
        guia_rapida_window = tk.Toplevel(self.root)
        guia_rapida_window.title("Guía Rápida del Programa")
        guia_rapida_window.geometry("565x320")
        guia_rapida_window.resizable(False, False)

        # Crear un Text widget para mostrar el mensaje de la guía rápida
        text_widget = tk.Text(guia_rapida_window, wrap="word", padx=10, pady=10)
        text_widget.pack(expand=True, fill="both")

        # Mensaje de la guía rápida
        mensaje_guia_rapida = (
            "📋 Guía Rápida del Programa\n\n"
            "1. Preparación de Carpetas\n"
            "• Carpetas limpias: Sin índice ni carpetas de anexos masivos\n"
            "• Nombres de archivos: Organizados mínimo secuencialmente\n"
            "• Radicado: Debe contener 23 dígitos\n\n"
            "2. Estructura de Carpetas\n"
            "🔹 Opción subcarpeta:\n"
            "   C01Principal/Archivos\n"
            "🔹 Opción 1 (Un expediente):\n"
            "   RADICADO/01PrimeraInstancia/C01Principal/Archivos\n"
            "🔹 Opción 2 (Varios expedientes):\n"
            "   SERIE_SUBSERIE/RADICADO/01PrimeraInstancia/C01Principal/Archivos\n\n"
            "3. Datos del SGDE\n"
            "• Use exactamente los mismos datos de 'Juzgado' y 'Serie/Subserie' registrados en migrador/validador y/o la TRD\n\n"
        )

        # Insertar el mensaje en el Text widget
        text_widget.insert(tk.END, mensaje_guia_rapida)
        text_widget.config(
            state=tk.DISABLED
        )  # Hacer que el Text widget sea de solo lectura

    def _on_radio_change(self, *args):
        self.selected_value = self.radio_var.get()
        self.logger.info(f"Opción seleccionada: {self.selected_value}")

        if self.selected_value == "1":
            self.label03.pack(side=tk.LEFT)
            self.entry03.pack(pady=5)
        else:
            self.label03.pack_forget()
            self.entry03.pack_forget()

    def _create_tooltips(self):
        """
        Crea tooltips para los radiobuttons usando imágenes.
        """
        image_paths = [
            self._get_bundled_path("assets/tooltip1.png"),
            self._get_bundled_path("assets/tooltip2.png"),
            self._get_bundled_path("assets/tooltip3.png"),
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
        csv_file_path = self._get_bundled_path(ruta)
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
        ruta_json = self._get_bundled_path("assets/last_version.json")
        with open(ruta_json, "r", encoding="utf-8") as file:
            data = json.load(file)
            version = data.get("version")
        return version

    def _comprobar_actualizaciones(self):
        url = "https://raw.githubusercontent.com/HammerDev99/GestionExpedienteElectronico_Version1/refs/heads/master/assets/last_version.json"  # O usa la URL de raw.githubusercontent.com
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
            cadena_rutas_invalidas = ""
            for i in carpetas:
                cadena_rutas_invalidas += "- "+i + "\n"
            if len(carpetas) > 1 and not tk.messagebox.askyesno(
                "Advertencia",
                f"Confirme si las siguientes carpetas son anexos anexos masivos:\n\n{cadena_rutas_invalidas}\n¿Desea continuar?",
            ):
                return
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

        if self.selected_value == "2": # and profundidad_maxima == 4:
            # Implementación del manejo de anexos masivos para opcion profundidad 4
            rutas_invalidas = self.validar_estructura_carpetas(
                estructura_directorios, self.selected_value
            )
            # Confirmación de carpetas de anexos masivos
            cadena_rutas_invalidas = ""
            for i in rutas_invalidas:
                cadena_rutas_invalidas += "- "+i + "\n"
            
            if cadena_rutas_invalidas == "" or tk.messagebox.askyesno(
                "Se encontraron anexos masivos", 
                f"Confirme si las siguientes carpetas son anexos anexos masivos:\n\n{cadena_rutas_invalidas}\n¿Desea continuar?"
            ):
                #**********************************
                #**********************************
                lista_cui, lista_subcarpetas, self.carpetas_omitidas = (
                    analyzer.obtener_lista_rutas_subcarpetas(
                        estructura_directorios, 4, folder_selected
                    )
                )
                #**********************************
                # Verificar si las listas están vacías o tienen valores por defecto de error
                # Analizar si se debe hacer la validación en este método o en obtener_rutas
                if not self._validar_estructura_expediente( # refactorizar esta función completamente
                    lista_cui, lista_subcarpetas, self.carpetas_omitidas
                ):

                    # Habilitar el envío de un mensaje con las carpetas que no cumplen con la estructura
                    # usar variable selected value y el diccionario folder_selected
                    #self.mostrar_lista_elementos_conflictivos(self.selected_value, estructura_directorios)

                    self.update_progressbar_status("")
                    self._restablecer_variables_clase()
                    return
                    #**********************************

                # Llamar al nuevo método para gestionar índices existentes
                continuar = self.gestionar_indices_existentes(folder_selected, analyzer)
                if not continuar:
                    return  # Detiene ejecución si se encontraron índices y no se eliminaron
                self.profundidad = 4

                #**********************************

                self.handle_directory_analysis(
                    folder_selected,
                    estructura_directorios,
                    lista_cui,
                    lista_subcarpetas,
                    self.carpetas_omitidas,
                    None,
                )
                self.lista_subcarpetas = lista_subcarpetas
                self.analyzer = analyzer
                if not self.lista_subcarpetas:
                    self.update_progressbar_status("")
                else:
                    self.update_progressbar_status("Listo para procesar")
            else:
                self._mostrar_rutas_invalidas(rutas_invalidas)
        elif self.selected_value == "3": # and profundidad_maxima == 5:
            # Implementación del manejo de anexos masivos para opcion profundidad 4
            rutas_invalidas = self.validar_estructura_carpetas(
                estructura_directorios, self.selected_value
            )
            # Confirmación de carpetas de anexos masivos
            cadena_rutas_invalidas = ""
            for i in rutas_invalidas:
                cadena_rutas_invalidas += "- "+i + "\n"
            if cadena_rutas_invalidas == "" or tk.messagebox.askyesno(
                "Se encontraron anexos masivos", 
                f"Confirme si las siguientes carpetas son anexos anexos masivos:\n\n{cadena_rutas_invalidas}"
            ):
                #**********************************
                #**********************************
                lista_cui, lista_subcarpetas, self.carpetas_omitidas = (
                    analyzer.obtener_lista_rutas_subcarpetas(
                        estructura_directorios, 5, None
                    )
                )
                #**********************************
                # Verificar si las listas están vacías o tienen valores por defecto de error
                # Analizar si se debe hacer la validación en este método o en obtener_rutas
                if not self._validar_estructura_expediente(
                    lista_cui, lista_subcarpetas, self.carpetas_omitidas
                ):

                    # Habilitar el envío de un mensaje con las carpetas que no cumplen con la estructura
                    # usar variable selected value y el diccionario folder_selected

                    self.update_progressbar_status("")
                    self._restablecer_variables_clase()
                    return
                    #**********************************
                # Llamar al nuevo método para gestionar índices existentes
                continuar = self.gestionar_indices_existentes(folder_selected, analyzer)
                if not continuar:
                    return  # Detiene ejecución si se encontraron índices y no se eliminaron
                self.profundidad = 5
                #**********************************

                self.handle_directory_analysis(
                    folder_selected,
                    estructura_directorios,
                    lista_cui,
                    lista_subcarpetas,
                    self.carpetas_omitidas,
                    analyzer,
                )
                self.lista_subcarpetas = lista_subcarpetas
                self.analyzer = analyzer
                if not self.lista_subcarpetas:
                    self.update_progressbar_status("")
                else:
                    self.update_progressbar_status("Listo para procesar")
            else:
                self._mostrar_rutas_invalidas(rutas_invalidas)
        else:
            # Adecuar esta parte para el caso de las carpetas que no cumplen con la estructura de niveles cuando sale el aviso "guia rápida" o advertencia
            tk.messagebox.showwarning(
                "Advertencia",
                "La estructura de directorios no coincide con la OPCIÓN seleccionada.\n\n"
                "Por favor, verifique la estructura interna de los directorios seleccionados.",
            )
            rutas_invalidas = self.validar_estructura_carpetas(
                estructura_directorios, self.selected_value
            )
            self.logger.warning(
                f"La estructura de los siguientes directorios no coincide con la OPCIÓN seleccionada: {rutas_invalidas}"
            )

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        """
        Busca y gestiona índices existentes.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada.
            analyzer (FolderAnalyzer): Instancia del analizador de carpetas.

        Returns:
            bool: True si se deben continuar las operaciones, False si se deben detener.
        """
        # Buscar y gestionar índices existentes
        indices = analyzer.buscar_indices_electronicos(folder_selected)
        if indices:
            indices_eliminados = self.confirmar_eliminar_indices(indices)
            if not indices_eliminados:
                self._restablecer_variables_clase()
                self.update_progressbar_status("")
                return False  # Detiene ejecución si se encontraron índices y no se eliminaron
        return (
            True  # Continúa ejecución si no se encontraron índices o si se eliminaron
        )

    def confirmar_eliminar_indices(self, indices):
        """
        Confirma con el usuario si desea eliminar los índices encontrados.
        """

        cantidad = len(indices)
        mensaje = f"Se encontraron {cantidad} índice{'s' if cantidad > 1 else ''} electrónico{'s' if cantidad > 1 else ''} que impide el procesamiento"
        if tk.messagebox.askyesno(
            "Índices Encontrados", f"{mensaje}. ¿Desea eliminarlos?"
        ):
            self.text_widget.insert(
                tk.END, "\n*******************\n✅ Índices eliminados:\n"
            )
            for indice in indices:
                try:
                    componentes = indice.split(os.sep)[-4:]
                    ruta_relativa = os.path.join(*componentes)
                    send2trash.send2trash(indice)
                    self.text_widget.insert(tk.END, f"   🔹 {ruta_relativa}\n")
                except Exception as e:
                    self.logger.error(f"Error eliminando índice {indice}: {str(e)}")
            self.text_widget.see(tk.END)
            return True
        else:
            self.text_widget.insert(tk.END, f"\n*******************\n❕ {mensaje}:\n")
            for indice in indices:
                # Obtener los últimos 4 componentes de la ruta
                componentes = indice.split(os.sep)[-4:]
                ruta_relativa = os.path.join(*componentes)
                self.text_widget.insert(tk.END, f"   🔹 {ruta_relativa}\n")
            self.text_widget.see(tk.END)
            return False

    def validar_estructura_carpetas(self, estructura_directorios, selected_value):
        """
        Valida la estructura de carpetas y retorna rutas inválidas.

        Args:
            estructura_directorios (dict): Diccionario con estructura de carpetas
            selected_value (str): Opción seleccionada ("2" o "3")

        Returns:
            list: Rutas que contienen subcarpetas no permitidas
        """
        rutas_invalidas = []
        nivel_maximo = self._obtener_nivel_maximo(selected_value)

        self._analizar_estructura(
            estructura_directorios, "", 0, nivel_maximo, rutas_invalidas
        )

        return rutas_invalidas

    def _obtener_nivel_maximo(self, selected_value):
        """Determina nivel máximo según opción seleccionada."""
        return 2 if selected_value == "2" else 3

    def _analizar_estructura(
        self, directorio, ruta_actual, nivel, nivel_maximo, rutas_invalidas
    ):
        """Analiza recursivamente la estructura buscando carpetas invalidas."""
        if not isinstance(directorio, dict):
            return

        if nivel >= nivel_maximo:
            self._verificar_subcarpetas(directorio, ruta_actual, rutas_invalidas)
            return

        for nombre, contenido in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre)
            self._analizar_estructura(
                contenido, nueva_ruta, nivel + 1, nivel_maximo, rutas_invalidas
            )

    def _verificar_subcarpetas(self, directorio, ruta_actual, rutas_invalidas):
        """Verifica si existen subcarpetas en el nivel actual."""
        for nombre, contenido in directorio.items():
            if isinstance(contenido, dict):
                rutas_invalidas.append(os.path.join(ruta_actual, nombre))

    def _mostrar_rutas_invalidas(self, rutas_invalidas):
        """Muestra las rutas inválidas en el widget de texto."""
        if rutas_invalidas:
            mensaje = "\n*******************\n⚠️ Las siguientes carpetas no cumplen con la estructura de niveles:\n"
            for ruta in rutas_invalidas:
                mensaje += f"- {ruta}\n"
            self.text_widget.insert(tk.END, mensaje)
            self.update_progressbar_status("")
            self.text_widget.see(tk.END)

    def _validar_cui(self, cui):
        """
        Valida que el CUI tenga exactamente 23 dígitos sin caracteres especiales.

        Args:
            cui (str): String a validar que puede contener números dispersos,
                    caracteres especiales y letras

        Returns:
            tuple: (bool, str) - (Es válido, CUI limpio)
                    - Es válido: True si se obtuvieron al menos 23 dígitos
                    - CUI limpio: Los primeros 23 dígitos encontrados o la cadena original
                                si no hay suficientes dígitos
        """
        try:
            # Extraer todos los dígitos de la cadena completa
            cui_limpio = "".join(c for c in cui if c.isdigit())

            # Verificar que tenga al menos 23 dígitos
            es_valido = len(cui_limpio) >= 23

            # Retornar los primeros 23 dígitos si hay suficientes,
            # o toda la cadena de dígitos si no hay 23
            return (es_valido, cui_limpio[:23] if es_valido else cui_limpio)

        except Exception as e:
            self.logger.error(f"Error al validar CUI '{cui}': {str(e)}")
            return False, cui

    def _mostrar_carpeta_seleccionada(self, folder_selected):
        """
        Muestra en el widget de texto la carpeta seleccionada.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada
        """
        self.text_widget.insert(
            tk.END,
            f"\n*******************\n❕ Carpeta seleccionada: {folder_selected}\n",
        )
        self.text_widget.see(tk.END)

    def _procesar_cuis(self, lista_cui, lista_subcarpetas):
        """
        Procesa y valida los CUIs de las carpetas.

        Args:
            lista_cui (list): Lista de CUIs
            lista_subcarpetas (list): Lista de subcarpetas

        Returns:
            tuple: Conjuntos de CUIs válidos e inválidos
        """
        cuis_validos = set()
        cuis_invalidos = set()

        if self.selected_value == "3":
            for sublista in lista_subcarpetas:
                for ruta in sublista:
                    cui = ruta.split("\\")[0]
                    self._validar_y_agregar_cui(cui, cuis_validos, cuis_invalidos)
        else:
            for cui in lista_cui:
                self._validar_y_agregar_cui(cui, cuis_validos, cuis_invalidos)

        return cuis_validos, cuis_invalidos

    def _validar_y_agregar_cui(self, cui, cuis_validos, cuis_invalidos):
        """
        Valida un CUI individual y lo agrega al conjunto correspondiente.

        Args:
            cui (str): CUI a validar
            cuis_validos (set): Conjunto de CUIs válidos
            cuis_invalidos (set): Conjunto de CUIs inválidos
        """
        es_valido, cui_procesado = self._validar_cui(cui)
        if es_valido:
            cuis_validos.add(cui_procesado)
        else:
            cuis_invalidos.add(cui)

    def _mostrar_carpetas_omitidas(self):
        """
        Muestra información sobre las carpetas que fueron omitidas por no cumplir con la estructura.
        """
        try:
            if self.carpetas_omitidas:
                # self._mensaje(None, f"Se encontraron {len(self.carpetas_omitidas)} carpetas que no cumplen con la estructura de directorios")

                text_aux = ".\n   🔹"
                mensaje_detalle = (
                    "❕ Las siguientes carpetas están vacías y no serán incluidas en el procesamiento:"
                    + text_aux[1:]
                )
                carpetas_omitidas_ordenadas = sorted(self.carpetas_omitidas)
                if carpetas_omitidas_ordenadas:
                    mensaje_detalle += text_aux.join(carpetas_omitidas_ordenadas[:-1])
                    if len(carpetas_omitidas_ordenadas) > 1:
                        mensaje_detalle += text_aux
                    mensaje_detalle += carpetas_omitidas_ordenadas[-1]  # + "."

                self.text_widget.insert(tk.END, mensaje_detalle + "\n")
                self.text_widget.see(tk.END)
        except Exception as e:
            self.logger.error(
                f"Error al mostrar las carpetas omitidas. No se eligio una estructura de carpetas adecuada: {str(e)}",
                exc_info=True,
            )

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui):
        """
        Muestra información sobre los CUIs que no cumplen con el formato requerido.

        Args:
            cuis_invalidos (set): Conjunto de CUIs inválidos
            lista_cui (list): Lista original de CUIs
        """
        text_aux = ".\n   🔹"
        if cuis_invalidos:
            # self._mensaje(None, "Algunas carpetas no cumplen con el formato requerido de 23 dígitos numéricos.")

            mensaje = "❕ Se encontraron radicados (CUI) que no tienen los 23 dígitos: "
            if self.selected_value == "3":
                cuis_invalidos_ordenados = sorted(cuis_invalidos)
                if cuis_invalidos_ordenados:
                    mensaje += text_aux.join(cuis_invalidos_ordenados[:-1])
                    if len(cuis_invalidos_ordenados) > 1:
                        mensaje += text_aux
                    mensaje += cuis_invalidos_ordenados[-1]  # + "\n"
            else:
                if lista_cui:
                    mensaje += ", ".join(lista_cui[:-1])
                    if len(lista_cui) > 1:
                        mensaje += ", "
                    mensaje += lista_cui[-1] + "."

            self.text_widget.insert(tk.END, mensaje + "\n")
            self.text_widget.see(tk.END)

    def handle_directory_analysis(
        self,
        folder_selected,
        estructura_directorios,
        lista_cui,
        lista_subcarpetas,
        carpetas_omitidas=None,
        analyzer=None,
    ):
        """
        Analiza y procesa la estructura de directorios seleccionada.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada
            estructura_directorios (dict): Estructura de directorios
            lista_cui (list): Lista de CUIs
            lista_subcarpetas (list): Lista de subcarpetas
            carpetas_omitidas (set, opcional): Conjunto de carpetas omitidas
            analyzer (FolderAnalyzer, opcional): Instancia del analizador de carpetas
        """
        
        # Este mensaje se esta viendo cada vez que se muestra en pantalla el mensaje de error de la guia rapida
        self._mostrar_carpeta_seleccionada(folder_selected)

        # Si no hay error, continuar con el resto del procesamiento...
        _cuis_validos, cuis_invalidos = self._procesar_cuis(
            lista_cui, lista_subcarpetas
        )

        # Actualizar atributos lista_subcarpetas de la clase
        self.lista_subcarpetas = lista_subcarpetas

        self._mostrar_carpetas_omitidas()

        self._mostrar_cuis_invalidos(cuis_invalidos, lista_cui)

    def _validar_estructura_expediente(
        self, lista_cui, lista_subcarpetas, carpetas_omitidas
    ):
        """
        Valida si la estructura del expediente es correcta verificando las listas generadas.

        Args:
            lista_cui (list): Lista de CUIs encontrados
            lista_subcarpetas (list): Lista de subcarpetas encontradas
            carpetas_omitidas (list/set): Carpetas omitidas durante el procesamiento

        Returns:
            bool: True si la estructura es válida, False si es inválida
        """
        # Verificar si las listas están vacías o tienen valores por defecto de error
        if (
            not lista_cui
            and not lista_subcarpetas
            and (not carpetas_omitidas or isinstance(carpetas_omitidas, set))
        ):

            self._mensaje(
                None,
                "❌ Error en la estructura de carpetas\n\n"
                "La estructura elegida no cumple con el formato requerido. Se detectaron archivos sueltos donde debería haber carpetas organizadas.\n\n"
                "Estructura esperada según la opción seleccionada:\n"
                "Opción 1: RADICADO/01PrimeraInstancia/C01Principal/Archivos\n"
                "Opción 2: SERIE_SUBSERIE/RADICADO/01PrimeraInstancia/C01Principal/Archivos\n\n"
                "📝 Recomendaciones:\n"
                "1. Verifique que seleccionó la opción correcta según su estructura de carpetas\n"
                "2. Asegúrese de que sus carpetas siguen exactamente la jerarquía mostrada arriba\n"
                "3. No incluya archivos sueltos en niveles donde debe haber carpetas\n"
                "4. No incluya carpetas de anexos masivos en el nivel de los archivos\n\n"
                "¿Necesita revisar el protocolo? Consulte la ayuda del sistema.",
            )
            return False

        return True

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
        if self.selected_value == "1":
            total_archivos = len(os.listdir(self.processor.get_ruta()))

        if not tk.messagebox.askyesno(
            message=f'Se procesarán {total_carpetas if self.selected_value != "1" else total_archivos} '
            f'{"cuadernos" if self.selected_value != "1" else "archivos"} que contiene la carpeta '
            f'"{os.path.basename(self.expediente) if self.selected_value != "1" else os.path.basename(self.processor.get_ruta())}". '
            f"¿Desea continuar?.",
            title=os.path.basename(self.expediente),
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
            self.processing_context.process_folder(self.selected_value, self.processor)
            self.processor = None
            self._restablecer_variables_clase()
            return
        # **********************************

        # Iniciar procesamiento
        if self.selected_value != "1":
            self.update_progressbar_status("")
            self.progress["value"] = 0.1
            self.text_widget.insert(tk.END, "\n🔄 Proceso iniciado...\n")
            self.update_idletasks()

        try:
            processed = 0
            for sublista in self.lista_subcarpetas:
                for ruta in sublista:
                    # Obtener RDO
                    if self.selected_value == "2":
                        rdo = os.path.normpath(os.path.basename(self.expediente))
                    else:
                        rdo = os.path.normpath(ruta)
                    rdo = self.analyzer._formater_cui(rdo)

                    # Actualizar GUI
                    self.text_widget.insert(
                        tk.END,
                        "- "
                        + os.path.normpath(
                            os.path.basename(self.expediente) + "/" + ruta
                        )
                        + "\n",
                    )
                    self.text_widget.see(tk.END)

                    # Procesar archivo
                    carpeta = self._get_bundled_path(
                        os.path.normpath(os.path.join(self.expediente, ruta))
                    )
                    processor = FileProcessor(
                        carpeta, "", despacho, subserie, rdo, logger=self.logger
                    )

                    # Procesar de forma asíncrona
                    await processor.process()

                    # Actualizar progreso
                    self.progress["value"] = 0.1 + (processed / total_carpetas) * 0.9
                    self.update_idletasks()
                    processed += 1

            # Finalizar procesamiento
            self.progress["value"] = 1.0
            self.update_idletasks()
            self._restablecer_variables_clase()
            self.update_progressbar_status("")
            self.text_widget.insert(
                tk.END, "✅ Proceso completado.\n*******************\n\n"
            )
            self._mensaje(1)
            self.progress["value"] = 0
            self.update_idletasks()

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}", exc_info=True)

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
        bundle_dir = (
            sys._MEIPASS
            if getattr(sys, "frozen", False)
            else os.path.abspath(os.path.dirname(__file__))
        )
        return os.path.normpath(os.path.join(bundle_dir, ruta))
