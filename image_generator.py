import os
from PIL import Image, ImageDraw, ImageFont

def create_tool_images(output_dir="assets/tools"):
    """
    Crea imágenes de placeholder para cada herramienta.
    
    Args:
        output_dir (str): Directorio donde se guardarán las imágenes.
    """
    # Asegurar que el directorio existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Configuración de herramientas
    tools = [
        {"name": "Crear Estructura de Carpetas", "color": "#4a7aaf", "filename": "folder_structure.png"},
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

if __name__ == "__main__":
    create_tool_images()
