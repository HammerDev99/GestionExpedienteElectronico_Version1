# coding=utf-8

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

class Application(ttk.Frame):

    expediente = ""
    carpetas = []
    is_updated = True
    selected_value = "2"
    lista_subcarpetas = []
    analyzer = None
    profundidad = None

    def __init__(self, root, logger=None):
        """
        @param: root tipo Tk; contiene la raíz de la aplicación Tkinter
        @modules: tkinter
        - Inicializa la aplicación, configura la ventana principal y crea los widgets.
        """
        self.root = root
        self.logger = logger or logging.getLogger('GUI')
        self.logger.info("Iniciando interfaz gráfica")
        self.profundidad = None
        try:
            super().__init__(root)
            root.title("GestionExpedienteElectronico")
            root.resizable(False, False)
            # root.geometry("350x300")
            root.protocol("WM_DELETE_WINDOW", self._on_closing)
            self.pack(padx=20, pady=20)  # Añadir padding aquí
            self.create_oneProcessWidgets()
        except Exception as e:
            self.logger.error(f"Error en inicialización GUI: {str(e)}", exc_info=True)
            raise

    def create_oneProcessWidgets(self):
        """
        @modules: tkinter
        - Crea y configura los widgets de la interfaz gráfica.
        """
        self.is_updated = self._comprobar_actualizaciones() # Comprobar actualizaciones al iniciar la aplicación

        self.label = tk.Label(self, text=r"Daniel Arbelaez Alvarez - HammerDev99", fg="blue", cursor="hand2")
        self.label.pack(side=tk.BOTTOM, padx=10, pady=10)
        self.label.bind(
            "<Button-1>",
            lambda e: self._callback(
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
                lambda e: self._callback(
                    "https://github.com/HammerDev99/GestionExpedienteElectronico_Version1/releases/tag/latest"
                ),
            )

        self.label01 = tk.Label(
            self, text="Juzgado", 
            font=("Helvetica", 12)
        )
        self.label01.pack(pady=5)

        self.entry01 = tk.Entry(self, width=90, justify="center")
        self.entry01.pack(pady=5)
        self.entry01.insert(0, "CENTRO DE SERVICIOS JUDICIALES DE BELLO")

        self.label02 = tk.Label(
            self, text="Serie o Subserie", 
            font=("Helvetica", 12)
        )
        self.label02.pack(pady=5)

        # Crear el Combobox para entry02
        self.entry02 = ttk.Combobox(self, width=90, state="normal", justify="center")
        self.entry02.pack(pady=5)

        # Leer el archivo CSV y obtener los valores para el Combobox
        self.load_csv_values()

        # Crear un Frame para los Radiobuttons
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=5)

        # Variable para los Radiobuttons
        self.radio_var = tk.StringVar(value="2")
        self.radio_var.trace("w", self._on_radio_change)

        # Crear los Radiobuttons
        """ self.radio1 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de una \nsola carpeta específica", variable=self.radio_var, value="1")
        self.radio1.pack(side=tk.LEFT, padx=10) """
        self.radio2 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de todas \nlas carpetas internas de un \nexpediente", variable=self.radio_var, value="2")
        self.radio2.pack(side=tk.LEFT, padx=10)
        self.radio3 = ttk.Radiobutton(self.radio_frame, text="Opción 2: Índice de múltiples \nexpedientes de una serie o \nsubserie documental", variable=self.radio_var, value="3")
        self.radio3.pack(side=tk.LEFT, padx=10)

        # Crear tooltips con imágenes para los Radiobuttons
        self._create_tooltips()

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

        self.text_widget.insert(tk.END, "Instrucciones de Uso del Programa\n\n1. Descargar la(s) carpeta(s): NO DEBEN TENER ÍNDICE.\n\n2. Validar esquema de carpetas: Asegúrate de que la estructura interna de carpetas cumple con el protocolo. Ejemplo:\n\n  -Opción 1: 05088/01PrimeraInstancia/C01Principal/Archivos\n  -Opción 2: SERIE_SUBSERIE/05088/01PrimeraInstancia/C01Principal/Archivos\n\n3. El radicado debe tener 23 dígitos y los nombres de los archivos deben tener un orden mínimo.\n\n4. Datos del SGDE: Ingresar exactamente los mismos datos de 'Juzgado' y 'serie o subserie' que registra en el SGDE.\n\n")

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

        # Barra de progreso
        self.progress = ttk.Progressbar(self, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=5)

        # Botón Aceptar
        self.aceptar = tk.Button(
            self, text="Aceptar", command=lambda: self.run_async_process(self), height=1, width=7
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

    def _on_radio_change(self, *args):
        self.selected_value = self.radio_var.get()
        self.logger.info(f"Opción seleccionada: {self.selected_value}")

    def _create_tooltips(self):
        """
        Crea tooltips para los radiobuttons usando imágenes.
        """
        image_paths = [
            self._get_bundled_path('assets/tooltip1.png'),
            self._get_bundled_path('assets/tooltip2.png'),
            self._get_bundled_path('assets/tooltip3.png')
        ]

        # Tooltip(self.radio1, image_paths[0])  # Comentado
        Tooltip(self.radio2, image_paths[1])
        Tooltip(self.radio3, image_paths[2])

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
            if tk.messagebox.askokcancel("Confirmar cierre", 
                                    "¿Está seguro que desea cerrar la aplicación?"):
                
                self.logger.debug("Usuario confirmó cierre de aplicación")
                
                # Limpiar recursos
                #self._cleanup()
                
                # Cerrar ventana principal y terminar aplicación
                self.root.quit()
                self.root.destroy()
                self.logger.info("Aplicación cerrada correctamente")
            else:
                self.logger.debug("Usuario canceló cierre de aplicación")
                
        except Exception as e:
            self.logger.error(f"Error al cerrar la aplicación: {str(e)}", exc_info=True)
            # Forzar cierre en caso de error
            self.root.destroy()

    def _cleanup(self):
        """
        Limpia recursos antes de cerrar.
        """
        try:
            self.logger.debug("Iniciando limpieza de recursos")
            
            # Cerrar procesos de Excel si existen
            if hasattr(self, 'analyzer') and self.analyzer:
                self.logger.debug("Cerrando procesos de Excel")
                # Implementar cierre de procesos Excel
            
            # Limpiar archivos temporales
            temp_files = ['temp_process_data.json', 'temp_excel_script.py']
            for file in temp_files:
                if os.path.exists(file):
                    try:
                        os.remove(file)
                        self.logger.debug(f"Archivo temporal eliminado: {file}")
                    except Exception as e:
                        self.logger.warning(f"No se pudo eliminar archivo temporal {file}: {str(e)}")
            
            # Restablecer variables
            self.expediente = ""
            self.carpetas = []
            self.lista_subcarpetas = []
            self.analyzer = None
            
            self.logger.debug("Limpieza de recursos completada")
            
        except Exception as e:
            self.logger.error(f"Error en limpieza de recursos: {str(e)}", exc_info=True)

    def load_csv_values(self):
        """
        Carga los valores del archivo CSV en el combobox.
        """
        csv_file_path = self._get_bundled_path('assets/TRD.csv')
        values = []
        
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                values.append(row['nombre'].upper())
                
        self.entry02['values'] = values
        if values:
            self.entry02.set(values[0])

    # Funcion para el caso de varias carpetas (4 y 5 niveles: carpeta/subcarpetas/archivos)
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

        folder_selected = os.path.normpath(filedialog.askdirectory())
        if folder_selected in [".", ""]:
            tk.messagebox.showwarning("Advertencia", "No se ha seleccionado ninguna carpeta.")
            return

        self.expediente = folder_selected

        analyzer = FolderAnalyzer({}, None)
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            tk.messagebox.showwarning("Advertencia", "La carpeta seleccionada está vacía o no es accesible.")
            return

        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        analyzer = FolderAnalyzer(estructura_directorios, profundidad_maxima)

        if self.selected_value == "2" and profundidad_maxima == 4:
            self.profundidad = 4
            lista_cui, lista_subcarpetas = analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 4, folder_selected)
            self.handle_directory_analysis(folder_selected, estructura_directorios, lista_cui, lista_subcarpetas, self.carpetas_omitidas, None)
            self.lista_subcarpetas = lista_subcarpetas
            self.analyzer = analyzer
        elif self.selected_value == "3" and profundidad_maxima == 5:
            self.profundidad = 5
            lista_cui, lista_subcarpetas = analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 5, None)
            self.handle_directory_analysis(folder_selected, estructura_directorios, lista_cui, 
            lista_subcarpetas, self.carpetas_omitidas, analyzer)
            self.lista_subcarpetas = lista_subcarpetas
            self.analyzer = analyzer
        else:
            tk.messagebox.showwarning(
                "Advertencia", 
                "La estructura de directorios no coincide con la OPCIÓN seleccionada.\n\n"
                "Por favor, verifique la estructura interna de los directorios seleccionados."
            )

    def _validar_cui(self, cui):
        """
        Valida que el CUI tenga exactamente 23 dígitos sin caracteres especiales.
        
        Args:
            cui (str): String a validar
            
        Returns:
            tuple: (bool, str) - (Es válido, CUI limpio)
        """
        # Eliminar espacios y cualquier texto después de estos
        cui = cui.split()[0]
        # Remover caracteres especiales y no numéricos
        cui_limpio = ''.join(c for c in cui if c.isdigit())
        # Verificar que tenga exactamente 23 dígitos
        return (len(cui_limpio) >= 23, cui_limpio[:23] if len(cui_limpio) >= 23 else cui)

    def _mostrar_carpeta_seleccionada(self, folder_selected):
        """
        Muestra en el widget de texto la carpeta seleccionada.
        
        Args:
            folder_selected (str): Ruta de la carpeta seleccionada
        """
        self.text_widget.insert(tk.END, f"\n*******************\nCarpeta seleccionada: {folder_selected}")
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
                    cui = ruta.split('\\')[0]
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

    def _actualizar_atributos_clase(self, lista_cui, lista_subcarpetas, estructura_directorios, analyzer):
        """
        Actualiza los atributos de la clase con los datos procesados.
        
        Args:
            lista_cui (list): Lista de CUIs
            lista_subcarpetas (list): Lista de subcarpetas
            estructura_directorios (dict): Estructura de directorios
            analyzer (FolderAnalyzer): Instancia del analizador de carpetas
        """
        try:
            self.lista_cui = lista_cui
            self.lista_subcarpetas = lista_subcarpetas
            self.estructura_directorios = estructura_directorios
            if self.selected_value == "3":
                self.carpetas_omitidas = analyzer.encontrar_cuis_faltantes(lista_cui, lista_subcarpetas)
        except Exception as e:
            self.logger.error(f"Error al guardar las listas en atributos de la clase: {str(e)}", exc_info=True)

    def _mostrar_carpetas_omitidas(self):
        """
        Muestra información sobre las carpetas que fueron omitidas por no cumplir con la estructura.
        """
        try:
            if self.carpetas_omitidas:
                mensaje_principal = f"Se encontraron {len(self.carpetas_omitidas)} carpetas que no cumplen con la estructura de directorios"
                self._mensaje(None, mensaje_principal)
                
                mensaje_detalle = "\n-Las siguientes carpetas no cumplen con la estructura de carpetas y no serán incluidas en el procesamiento:\n"
                mensaje_detalle += " ".join(f"{carpeta}, " for carpeta in sorted(self.carpetas_omitidas))
                
                self.text_widget.insert(tk.END, mensaje_detalle + "\n")
                self.text_widget.see(tk.END)
        except Exception as e:
            self.logger.error(f"Error al mostrar las carpetas omitidas. No se eligio una estructura de carpetas adecuada: {str(e)}", exc_info=True)

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui):
        """
        Muestra información sobre los CUIs que no cumplen con el formato requerido.
        
        Args:
            cuis_invalidos (set): Conjunto de CUIs inválidos
            lista_cui (list): Lista original de CUIs
        """
        if cuis_invalidos:
            mensaje = "- Se encontraron carpetas que no cumplen con el formato de 23 dígitos:\n"
            if self.selected_value == "3":
                mensaje += " ".join(f"{cui}, " for cui in sorted(cuis_invalidos))
            else:
                mensaje += " ".join(f"{cui}, " for cui in lista_cui)
                
            self.text_widget.insert(tk.END, mensaje)
            self.text_widget.see(tk.END)
            self._mensaje(None, "Algunas carpetas no cumplen con el formato requerido de 23 dígitos numéricos.")

    def handle_directory_analysis(self, folder_selected, estructura_directorios, lista_cui, lista_subcarpetas, carpetas_omitidas=None, analyzer=None):
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
        self._mostrar_carpeta_seleccionada(folder_selected)
        
        _, cuis_invalidos = self._procesar_cuis(lista_cui, lista_subcarpetas)
        
        self._actualizar_atributos_clase(lista_cui, lista_subcarpetas, estructura_directorios, analyzer)
        
        self._mostrar_carpetas_omitidas()
        
        self._mostrar_cuis_invalidos(cuis_invalidos, lista_cui)

    def run_async_process(self, app):
        """Inicia el procesamiento asíncrono"""
        asyncio.run(app.procesa_expedientes())

    async def procesa_expedientes(self):
        """Versión asíncrona simplificada del procesamiento de expedientes"""
        if not self.lista_subcarpetas:
            self._mensaje(3)
            return

        self.logger.info(f"Procesando {len(self.lista_subcarpetas)} expedientes")
        total_carpetas = sum(len(sublista) for sublista in self.lista_subcarpetas)
        self.progress["maximum"] = 1  # La barra de progreso va de 0 a 1

        # Confirmar procesamiento
        if not tk.messagebox.askyesno(
                message=f'Se procesarán {total_carpetas} carpetas que contiene la carpeta {os.path.basename(self.expediente)}". \n¿Desea continuar?.',
                title=os.path.basename(self.expediente)):
            self.expediente = ""
            self.carpetas = []
            self._mensaje(6)
            return

        # Iniciar procesamiento
        self.progress["value"] = 0.1
        self.text_widget.insert(tk.END, "\n\nProceso iniciado...\n")
        self.update_idletasks()

        try:
            processed = 0
            for sublista in self.lista_subcarpetas:
                despacho = self.entry01.get()
                subserie = self.entry02.get()
                
                for ruta in sublista:
                    # Obtener RDO
                    if self.selected_value == "2":
                        rdo = os.path.normpath(os.path.basename(self.expediente))
                    else:
                        rdo = os.path.normpath(ruta)
                    rdo = self.analyzer._formater_cui(rdo)

                    # Actualizar GUI
                    self.text_widget.insert(tk.END, "- "+os.path.normpath(os.path.basename(self.expediente)+"/"+ruta)+"\n")
                    self.text_widget.see(tk.END)

                    # Procesar archivo
                    carpeta = self._get_bundled_path(os.path.normpath(os.path.join(self.expediente, ruta)))
                    processor = FileProcessor(carpeta, "", despacho, subserie, rdo, logger=self.logger)
                    
                    # Procesar de forma asíncrona
                    await processor.process()

                    # Actualizar progreso
                    self.progress["value"] = 0.1 + (processed  / total_carpetas) * 0.9
                    self.update_idletasks()
                    processed += 1

            # Finalizar procesamiento
            self.progress["value"] = 1.0
            self.update_idletasks()
            self._cleanup_state()
            self.text_widget.insert(tk.END, "Proceso completado.\n*******************\n")
            self.progress["value"] = 0
            self.update_idletasks()
            self._mensaje(1)

        except Exception as e:
            self.logger.error(f"Error en procesamiento: {str(e)}", exc_info=True)

    def _cleanup_state(self):
        """Limpia el estado de la aplicación"""
        self.expediente = ""
        self.carpetas = []
        self.lista_cui = []
        self.lista_subcarpetas = []
        self.estructura_directorios = {}
        self.analyzer = None

    def _mensaje(self, result = None, mensaje = None):
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
            6: "Procedimiento detenido"
        }
        if result != None:
            tk.messagebox.showinfo(
                message=switcher.get(result), title=os.path.basename(self.expediente)
            )
            self.text_widget.insert(tk.END, "\n")
            self.logger.info(result, exc_info=True)
        
        if mensaje != None:
            tk.messagebox.showinfo(
                message=mensaje, title=os.path.basename(self.expediente)
            )
            self.logger.info(result, exc_info=True)

    def _get_bundled_path(self, ruta):
        """
        Obtiene la ruta correcta según el entorno de ejecución.
        
        Args:
            ruta (str): Ruta relativa al directorio base
            
        Returns:
            str: Ruta absoluta normalizada
        """
        bundle_dir = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.dirname(__file__))
        return os.path.normpath(os.path.join(bundle_dir, ruta))

    def _obtener_version_actual(self):
        # Determinar la ruta del archivo xlsm
        ruta_json = self._get_bundled_path('assets/last_version.json')
        with open(ruta_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
            version = data.get('version')
        return version

    def _comprobar_actualizaciones(self):
        url = "https://raw.githubusercontent.com/HammerDev99/GestionExpedienteElectronico_Version1/refs/heads/master/assets/last_version.json"  # O usa la URL de raw.githubusercontent.com
        try:
            response = requests.get(url)
            response.raise_for_status()
            datos = response.json()

            version_actual = list(map(int, self._obtener_version_actual().split(".")))
            ultima_version = list(map(int, datos.get('version').split(".")))

            if version_actual < ultima_version:
                # Actualizar variable para mostrar notificación en un label de la GUI
                return False # la variable is_updated se actualiza a False
            else:
                return True # la variable is_updated se mantiene en True
        except requests.RequestException as e:
            self.logger.error(f"Error al comprobar actualizaciones: {e}", exc_info=True)
