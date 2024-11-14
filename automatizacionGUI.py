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
from carpetas_analyzer import CarpetasAnalyzer
from tooltip import Tooltip

import csv

class Application(ttk.Frame):

    expediente = ""
    carpetas = []
    is_updated = True
    selected_value = "2"
    lista_subcarpetas = []
    analyzer = None

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

        # El radicado se obtendrá mediante la selección del usuario sobre la estructura de carpetas que tenga
        """ # Label y entry para la variable rdo
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
        self.label1.pack(pady=1) """

        # Crear un Frame para los Radiobuttons
        self.radio_frame = tk.Frame(self)
        self.radio_frame.pack(pady=5)

        # Variable para los Radiobuttons
        self.radio_var = tk.StringVar(value="2")
        self.radio_var.trace("w", self.on_radio_change)

        # Crear los Radiobuttons
        """ self.radio1 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de una \nsola carpeta específica", variable=self.radio_var, value="1")
        self.radio1.pack(side=tk.LEFT, padx=10) """
        self.radio2 = ttk.Radiobutton(self.radio_frame, text="Opción 1: Índice de todas \nlas carpetas internas de un \nexpediente", variable=self.radio_var, value="2")
        self.radio2.pack(side=tk.LEFT, padx=10)
        self.radio3 = ttk.Radiobutton(self.radio_frame, text="Opción 2: Índice de múltiples \nexpedientes de una serie o \nsubserie documental", variable=self.radio_var, value="3")
        self.radio3.pack(side=tk.LEFT, padx=10)

        # Crear tooltips con imágenes para los Radiobuttons
        self.create_tooltips()

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

        self.text_widget.insert(tk.END, "Instrucciones de Uso del Programa\n\n1. Descargar la(s) carpeta(s): NO DEBEN TENER ÍNDICE.\n\n2. Validar esquema de carpetas: Asegúrate de que la estructura interna de carpetas cumple con el protocolo. Ejemplo:\n\n  -Opción 1: 05088/01PrimeraInstancia/C01Principal/Archivos\n  -Opción 2: 2024/05088/01PrimeraInstancia/C01Principal/Archivos\n\n3. El radicado debe tener 23 dígitos y los nombres de los archivos deben tener un orden mínimo.\n\n4. Datos del SGDE: Ingresar exactamente los mismos datos de 'Juzgado' y 'serie o subserie' que registra en el SGDE.\n\n")

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
            self, text="Aceptar", command=self.procesa_expedientes, height=1, width=7
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

    def on_radio_change(self, *args):
        self.selected_value = self.radio_var.get()
        #print(f"El valor del Radiobutton ha cambiado a: {selected_value}")

    def get_radio_value(self):
        selected_value = self.radio_var.get()
        print(f"Valor seleccionado: {selected_value}")

    def create_tooltips(self):
        # Determinar la ruta del archivo xlsm
        if getattr(sys, 'frozen', False):
            # Si se está ejecutando el archivo empaquetado
            bundle_dir = sys._MEIPASS
        else:
            # Si se está ejecutando desde el script original
            bundle_dir = os.path.abspath(os.path.dirname(__file__))

        image_paths = [
            os.path.join(bundle_dir, 'assets/tooltip1.png'),
            os.path.join(bundle_dir, 'assets/tooltip2.png'), 
            os.path.join(bundle_dir, 'assets/tooltip3.png')
        ]
        #print(image_paths)
        """ Tooltip(self.radio1, image_paths[0]) """
        Tooltip(self.radio2, image_paths[1])
        Tooltip(self.radio3, image_paths[2])

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

    def load_csv_values(self):
        # Determinar la ruta del archivo xlsm
        if getattr(sys, 'frozen', False):
            # Si se está ejecutando el archivo empaquetado
            bundle_dir = sys._MEIPASS
        else:
            # Si se está ejecutando desde el script original
            bundle_dir = os.path.abspath(os.path.dirname(__file__))

        csv_file_path = os.path.join(bundle_dir, 'assets/TRD.csv')
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

        analyzer = CarpetasAnalyzer({}, None)
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            tk.messagebox.showwarning("Advertencia", "La carpeta seleccionada está vacía o no es accesible.")
            return

        #print("Estructura de Directorios:", estructura_directorios)
        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        analyzer = CarpetasAnalyzer(estructura_directorios, profundidad_maxima)

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

        # Imprimir las listas para verificación
        """ print("Estructura de Directorios:", self.estructura_directorios)
        print("Lista de C.U.I.:", self.lista_cui)
        print("Lista de Subcarpetas Internas:", self.lista_subcarpetas)
        print("Carpetas Omitidas:", self.carpetas_omitidas) """

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
        #print(f"CUI: {cui}")
        # Remover caracteres especiales y no numéricos
        cui_limpio = ''.join(c for c in cui if c.isdigit())
        #print(f"CUI limpio: {cui_limpio}")
        # Verificar que tenga exactamente 23 dígitos
        return (len(cui_limpio) >= 23, cui_limpio[:23] if len(cui_limpio) >= 23 else cui)

    def handle_directory_analysis(self, folder_selected, estructura_directorios, lista_cui, lista_subcarpetas, carpetas_omitidas = None, analyzer = None):
        """
        @param: folder_selected tipo str, estructura_directorios tipo dict, lista_cui tipo list, lista_subcarpetas tipo list, carpetas_omitidas tipo set

        Muestra mensaje de carpeta seleccionada
        Guarda las listas en atributos de la clase
        Muestra mensaje de carpetas omitidas
        """
        self.text_widget.insert(tk.END, f"\n\nCarpeta seleccionada: {folder_selected}\n")
        self.text_widget.see(tk.END)

        # Conjuntos para almacenar CUIs válidos e inválidos
        cuis_validos = set()
        cuis_invalidos = set()

        # Procesar cada sublista en lista_subcarpetas
        if self.selected_value == "3":
            for sublista in lista_subcarpetas:
                for ruta in sublista:
                    # Obtener la parte antes del primer backslash
                    cui = ruta.split('\\')[0]
                    
                    # Validar el CUI
                    es_valido, cui_procesado = self._validar_cui(cui)
                    if es_valido:
                        cuis_validos.add(cui_procesado)
                    else:
                        cuis_invalidos.add(cui)
        else:
            for cui in lista_cui:
                es_valido, cui_procesado = self._validar_cui(cui)
                if es_valido:
                    cuis_validos.add(cui_procesado)
                else:
                    cuis_invalidos.add(cui)

        # Actualiza las listas en atributos de la clase
        try:
            self.lista_cui = lista_cui
            self.lista_subcarpetas = lista_subcarpetas
            self.estructura_directorios = estructura_directorios
            if self.selected_value == "3":
                self.carpetas_omitidas = analyzer.encontrar_cuis_faltantes(lista_cui, lista_subcarpetas)
        except Exception as e:
            print(f"Error al guardar las listas en atributos de la clase: {str(e)}")
        
        # Mostrar carpetas omitidas
        try:
            if self.carpetas_omitidas:
                mensaje = f"Se encontraron {len(self.carpetas_omitidas)} carpetas que no cumplen con la estructura de directorios"
                self.mensaje(None, mensaje)
                mensaje = "Las siguientes carpetas no cumplen con la estructura de carpetas y no serán incluidas en el procesamiento:\n"
                for carpeta in sorted(self.carpetas_omitidas):
                    mensaje += f"- {carpeta}\n"
                self.text_widget.insert(tk.END, mensaje + "\n")
                self.text_widget.see(tk.END)
        except Exception as e:
            print(f"Error al mostrar las carpetas omitidas: {str(e)}. No se eligio una estructura de carpetas adecuada")

        # Muestra los CUIs inválidos
        if cuis_invalidos:
            mensaje = "Se encontraron carpetas que no cumplen con el formato de 23 dígitos:\n"
            if self.selected_value == "3":
                for cui in sorted(cuis_invalidos):
                    mensaje += f"- {cui}\n"
            else:
                for cui in lista_cui:
                    mensaje += f"- {cui}\n"
            self.text_widget.insert(tk.END, mensaje)
            self.text_widget.see(tk.END)
            self.mensaje(None, "Algunas carpetas no cumplen con el formato requerido de 23 dígitos numéricos.")

    def procesa_expedientes(self):
        """
        - Obtiene Lista de Subcarpetas Internas para procesar
        - Valida radicados unicamente obteniendo los primeros 23 digitos
        - Confirma procedimiento con el usuario
        - Crea objeto y llama metodo procesaCarpetas() u otro en su defecto para cada expediente en la lista
        - Genera reporte de lista de rutas procesadas
        """
        lista_subcarpetas = self.lista_subcarpetas
        analyzer = self.analyzer

        total_carpetas = sum(len(sublista) for sublista in lista_subcarpetas)
        self.progress["maximum"] = 1  # La barra de progreso va de 0 a 1

        if lista_subcarpetas != []:	
            num_carpetas = total_carpetas
            if tk.messagebox.askyesno(
                    message=f'Se procesarán {num_carpetas} carpetas que contiene la carpeta "{os.path.basename(self.expediente)}". \n¿Desea continuar?.',
                    title=os.path.basename(self.expediente),
                ):
                # Indicar al usuario que el proceso ha comenzado
                self.progress["value"] = 0.1
                self.text_widget.insert(tk.END, "\nProceso iniciado...\n")
                # self.text_widget.insert(tk.END, "CARPETAS PROCESADAS:\n")
                self.update_idletasks()

                i = 0
                for sublista in lista_subcarpetas:
                    # Obtiene el nombre del despacho judicial del campo de entrada
                    despacho = self.entry01.get()
                    # Obtiene la serie o subserie documental del combobox
                    subserie = self.entry02.get()
                    for ruta in sublista:
                        i = i + 1
                        
                        # Validacion de datos en consola
                        #print("Despacho: ", despacho)
                        #print("Subserie: ", subserie)   
                        #print("sublista: ", sublista)
                        #print("Ruta: ", ruta)

                        # Obtiene el valor del radicado
                        if self.selected_value == "2":
                            rdo = os.path.normpath(os.path.basename(self.expediente))
                            print("Radicado antes: ", rdo)
                            rdo = analyzer._formater_cui(rdo)
                            print("Radicado después: ", rdo)
                        elif self.selected_value == "3":
                            rdo = os.path.normpath(ruta)
                            print("Radicado antes: ", rdo)
                            rdo = analyzer._formater_cui(rdo)
                            print("Radicado después: ", rdo)
                        print("Radicado: ", rdo)

                        # Muestra en el widget de texto la ruta subserie/radicado
                        self.text_widget.insert(tk.END, "- "+os.path.normpath(os.path.basename(self.expediente)+"/"+ruta)+"\n")
                        # Asegura que el último texto insertado sea visible
                        self.text_widget.see(tk.END)

                        # Concatena la ruta con la carpeta a procesar y normaliza la ruta
                        carpeta = os.path.normpath(self.expediente+"/"+ruta)

                        # Crea una instancia de AutomatizacionEmpleado con los parámetros necesarios
                        #obj = AutomatizacionEmpleado(carpeta, "", despacho, subserie, rdo)
                        # Ejecuta el procesamiento de la carpeta
                        #obj.process()

                        # Actualiza la barra de progreso basado en el progreso actual (10% inicial + progreso proporcional)
                        self.progress["value"] = 0.1 + ((i + 1) / total_carpetas) * 0.9
                        # Actualiza la interfaz gráfica para mostrar el progreso
                        self.update_idletasks()

                # Indicar al usuario que el proceso ha terminado
                self.progress["value"] = 1.0  # Asegurarse de que la barra de progreso llegue al 100%
                self.update_idletasks()
                self.expediente = ""
                self.carpetas = []
                self.text_widget.insert(tk.END, "Proceso completado.\n*******************\n")
                self.update_idletasks()
                self.mensaje(1)
            else:
                self.expediente = ""
                self.carpetas = []
                self.mensaje(6)
        else:
            self.mensaje(3)

    def mensaje(self, result = None, mensaje = None):
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
            6: "Procedimiento detenido"
        }
        if result != None:
            tk.messagebox.showinfo(
                message=switcher.get(result), title=os.path.basename(self.expediente)
            )
            self.text_widget.insert(tk.END, "\n")
            # self.text_widget.insert(tk.END, switcher.get(result))
            lista_vacia = list()
            self.agregaNombreBase(lista_vacia, False)
        
        if mensaje != None:
            tk.messagebox.showinfo(
                message=mensaje, title=os.path.basename(self.expediente)
            )

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