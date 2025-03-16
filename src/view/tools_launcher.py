from PIL import Image, ImageDraw, ImageFont, ImageTk
from tkinter import ttk
import logging
import os
import sys
import tkinter as tk
import webbrowser

if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.utils.resource_manager import resource_manager
else:
    # Entorno de desarrollo
    from utils.resource_manager import resource_manager

def create_tool_images(output_dir="src/assets/tools"):
    
    #Crea imágenes de placeholder para cada herramienta.
    
    #Args:
    #    output_dir (str): Directorio donde se guardarán las imágenes.

    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Configuración de herramientas
    tools = [
        {"name": "Crear Estructura de Carpetas", "color": "#4a7aaf", "filename": "Banco1.png"},
        {"name": "Renombrador de Archivos", "color": "#5c9657", "filename": "file_renamer.png"},
        {"name": "Validador de Índices", "color": "#d17a47", "filename": "index_validator.png"},
        {"name": "Conversor de Documentos", "color": "#7b539c", "filename": "document_converter.png"},
        {"name": "Extractor de Metadatos", "color": "#c23b3b", "filename": "metadata_extractor.png"},
        {"name": "Asistente de Migración", "color": "#35a2b5", "filename": "migration_assistant.png"}
    ]
    
    # Crear cada imagen
    for tool in tools:
        # Crear imagen con el color de fondo de la herramienta
        img = Image.new('RGB', (350, 150), tool["color"])
        draw = ImageDraw.Draw(img)
        
        # Intentar cargar una fuente, usar default si falla
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        
        # Añadir texto centrado
        text = tool["name"]
        text_width, text_height = draw.textsize(text, font=font)
        position = ((350 - text_width) // 2, (150 - text_height) // 2)
        draw.text(position, text, fill="white", font=font)
        
        # Guardar imagen
        img_path = os.path.join(output_dir, tool["filename"])
        img.save(img_path)
        print(f"Imagen creada: {img_path}")


class ToolsLauncher:
    
    #Ventana emergente que muestra un banco de herramientas complementarias para AgilEx, con botones e imágenes que redirigen a las descargas.

    
    def __init__(self, parent=None, logger=None):
        # Configurar logger
        self.logger = logger or logging.getLogger(__name__)
        
        # Crear ventana principal si no se proporciona una ventana padre
        if parent is None:
            self.root = tk.Tk()
            self.root.title("Banco de Herramientas - AgilEx")
        else:
            self.root = tk.Toplevel(parent)
            self.root.title("Banco de Herramientas - AgilEx")
            
        # Configurar ventana
        self.root.geometry("810x600")
        self.root.resizable(False, False)
        self.configure_styles()
        
        # Lista de herramientas
        self.tools = [
            {
                "name": "Crear Estructura de Carpetas",
                "description": "Organiza expedientes judiciales generando automáticamente la estructura estándar (01PrimeraInstancia/C01Principal) y transfiere los documentos desde la carpeta única original hacia C01Principal, cumpliendo con el protocolo de organización documental establecido.",
                "image": "Banco1.png",
                "url": "https://enki.care/Banco_Crear_Estructura_Carpetas",
                "color": "#4a7aaf"
            }]
        """ ,
            {
                "name": "Renombrador de Archivos",
                "description": "Renombra archivos masivamente siguiendo el formato requerido para expedientes electrónicos.",
                "image": "file_renamer.png",
                "url": "https://github.com/HammerDev99/GestionExpedienteElectronico_Tools/releases/download/file-renamer/renombrador_archivos.exe",
                "color": "#5c9657"
            },
            {
                "name": "Validador de Índices",
                "description": "Verifica la integridad de los índices electrónicos contra los archivos existentes.",
                "image": "index_validator.png",
                "url": "https://github.com/HammerDev99/GestionExpedienteElectronico_Tools/releases/download/index-validator/validador_indices.exe",
                "color": "#d17a47"
            },
            {
                "name": "Conversor de Documentos",
                "description": "Convierte diferentes formatos de documentos a PDF para mayor compatibilidad.",
                "image": "document_converter.png",
                "url": "https://github.com/HammerDev99/GestionExpedienteElectronico_Tools/releases/download/doc-converter/conversor_documentos.exe",
                "color": "#7b539c"
            },
            {
                "name": "Extractor de Metadatos",
                "description": "Extrae y visualiza los metadatos de los archivos para validación.",
                "image": "metadata_extractor.png",
                "url": "https://github.com/HammerDev99/GestionExpedienteElectronico_Tools/releases/download/metadata-tool/extractor_metadatos.exe",
                "color": "#c23b3b"
            },
            {
                "name": "Asistente de Migración",
                "description": "Facilita la migración de expedientes entre diferentes sistemas de gestión documental.",
                "image": "migration_assistant.png",
                "url": "https://github.com/HammerDev99/GestionExpedienteElectronico_Tools/releases/download/migration-tool/asistente_migracion.exe",
                "color": "#35a2b5"
            }
        ] """
        
        # Crear interfaz
        self.create_widgets()
        
    TOOL_BUTTON_STYLE = "ToolButton.TButton"

    def configure_styles(self):
        # Configura los estilos personalizados para la interfaz
        style = ttk.Style()
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        style.configure("CardTitle.TLabel", background="white", font=("Helvetica", 12, "bold"))
        style.configure("CardDesc.TLabel", background="white", font=("Helvetica", 10))
        style.configure(self.TOOL_BUTTON_STYLE, font=("Helvetica", 10, "bold"))
        
    def create_widgets(self):
        #Crea todos los widgets de la interfaz
        # Frame principal con scrollbar
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título y descripción
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame, 
            text="Banco de Herramientas Complementarias", 
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(anchor=tk.CENTER)
        
        desc_label = ttk.Label(
            title_frame,
            text="Estas herramientas facilitan el trabajo con expedientes electrónicos y complementan las funcionalidades de AgilEx.",
            font=("Helvetica", 10),
            wraplength=780
        )
        desc_label.pack(anchor=tk.CENTER, pady=(5, 0))
        
        # Canvas con scrollbar para las tarjetas de herramientas
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
        tools_frame = ttk.Frame(canvas)
        
        # Configurar scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Crear ventana en el canvas para el frame
        canvas.create_window((0, 0), window=tools_frame, anchor=tk.NW)
        tools_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Crear tarjetas para cada herramienta
        row, col = 0, 0
        for i, tool in enumerate(self.tools):
            self.create_tool_card(tools_frame, tool, row, col)
            col += 1
            if col > 1:  # 2 tarjetas por fila
                col = 0
                row += 1
        close_button = ttk.Button(
            self.root, 
            text="Cerrar", 
            command=self.close_window,
            style=self.TOOL_BUTTON_STYLE
        )
        close_button.pack(side=tk.BOTTOM, pady=10)
        
        # Vincular scroll con rueda del ratón
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Etiqueta de copyright
        #copyright_label = ttk.Label(
        #    self.root,
        #    text="© 2025 Daniel Arbeláez - HammerDev99",
        #    font=("Helvetica", 8)
        #)
        #copyright_label.pack(side=tk.BOTTOM, pady=(0, 5))
        
    def create_tool_card(self, parent, tool, row, col):
        #Crea una tarjeta para una herramienta específica
        # Frame para la tarjeta
        card_frame = ttk.Frame(parent, style="Card.TFrame")
        card_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Contenedor para la imagen
        img_container = ttk.Frame(card_frame, width=350, height=150)
        img_container.pack(fill=tk.X, padx=10, pady=10)
        img_container.pack_propagate(False)
        
        # Cargar la imagen (placeholder o desde URL)
        try:
            img_path = resource_manager.get_path(f"src/assets/tools/{tool['image']}") 
                
            if os.path.exists(img_path):
                img = Image.open(img_path)
            else:
                # Crear imagen placeholder con el color de la herramienta
                img = Image.new('RGB', (350, 150), tool['color'])
                
            # Redimensionar imagen
            img = img.resize((350, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Mostrar imagen
            img_label = ttk.Label(img_container, image=photo)
            img_label.image = photo  # Guardar referencia
            img_label.pack(fill=tk.BOTH)
            
        except Exception as e:
            self.logger.error(f"Error cargando imagen para {tool['name']}: {str(e)}")
            # Crear placeholder en caso de error
            placeholder = ttk.Label(
                img_container, 
                text=tool['name'],
                background=tool['color'],
                foreground="white",
                font=("Helvetica", 14, "bold")
            )
            placeholder.pack(fill=tk.BOTH, expand=True)
        
        # Información de la herramienta
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Título
        title_label = ttk.Label(
            info_frame, 
            text=tool['name'],
            style="CardTitle.TLabel"
        )
        title_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Descripción
        desc_label = ttk.Label(
            info_frame,
            text=tool['description'],
            style="CardDesc.TLabel",
            wraplength=330
        )
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        download_button = ttk.Button(
            info_frame,
            text="Descargar",
            command=lambda t=tool: self.open_url(t['url']),
            style=self.TOOL_BUTTON_STYLE
        )
        download_button.pack(anchor=tk.E)
    
    def open_url(self, url):
        #Abre una URL en el navegador predeterminado
        try:
            self.logger.info(f"Abriendo URL: {url}")
            webbrowser.open_new(url)
        except Exception as e:
            self.logger.error(f"Error abriendo URL: {str(e)}")
            tk.messagebox.showerror("Error", f"No se pudo abrir la URL:\n{url}\n\nError: {str(e)}")
    
    def close_window(self):
        #Cierra la ventana
        if isinstance(self.root, tk.Toplevel):
            self.root.destroy()
        else:
            self.root.quit()
    
    def run(self):
        #Inicia el bucle principal si es una ventana independiente
        if not isinstance(self.root, tk.Toplevel):
            self.root.mainloop()
