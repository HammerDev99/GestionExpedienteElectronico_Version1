# resource_manager.py

import logging
import os
import sys
import tempfile

class ResourceManager:
    """
    Gestor de recursos genérico para aplicaciones Python.

    - Funciona tanto en entornos de desarrollo como en aplicaciones empaquetadas
    - No impone ninguna estructura de directorios específica
    - Preserva la estructura exacta de rutas definida en el archivo spec
    """

    APP_DATA_FOLDER = "AgilEx"
    
    def __init__(self, logger=None):
        """
        Inicializa el gestor de recursos.
        
        Args:
            logger: Objeto logger opcional para registrar mensajes
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Determinar el entorno de ejecución
        self.is_frozen = getattr(sys, "frozen", False)
        
        # Obtener la ruta base según el entorno
        if self.is_frozen:
            # En una aplicación empaquetada con PyInstaller
            self.base_path = sys._MEIPASS
        else:
            # En entorno de desarrollo
            # Asumimos que resource_manager.py está en src/utils
            self.base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
        if logger:
            logger.info(f"ResourceManager inicializado. Base path: {self.base_path}")
    
    def get_path(self, relative_path):
        """
        Obtiene la ruta completa a un recurso respetando la estructura de directorios.

        Args:
            relative_path (str): Ruta relativa al recurso

        Returns:
            str: Ruta absoluta al recurso
        """
        # Normalizar separadores de ruta para el sistema operativo actual
        normalized_path = relative_path.replace('/', os.sep).replace('\\', os.sep)

        # Construir la ruta completa
        full_path = os.path.join(self.base_path, normalized_path)

        # Normalizar la ruta final
        result = os.path.normpath(full_path)

        if self.logger:
            self.logger.debug(f"Resource path: {relative_path} -> {result}")

        return result

    def get_writable_path(self, subdir=""):
        """
        Obtiene una ruta escribible para datos generados en ejecución.

        A diferencia de get_path (recursos de solo lectura del bundle),
        esta ruta admite escritura. Necesario porque la aplicación se
        instala en Program Files, donde el directorio de la app es de
        solo lectura.

        Args:
            subdir (str): Subdirectorio opcional (ej. "logs")

        Returns:
            str: Ruta absoluta a un directorio existente y escribible
        """
        candidates = []

        if self.is_frozen:
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                candidates.append(
                    os.path.join(local_app_data, self.APP_DATA_FOLDER)
                )
        else:
            candidates.append(os.getcwd())

        candidates.append(
            os.path.join(tempfile.gettempdir(), self.APP_DATA_FOLDER)
        )

        for candidate in candidates:
            target = os.path.join(candidate, subdir) if subdir else candidate
            try:
                os.makedirs(target, exist_ok=True)
                return os.path.normpath(target)
            except (OSError, PermissionError) as e:
                if self.logger:
                    self.logger.warning(
                        f"Ruta no escribible {target}: {e}"
                    )

        return tempfile.gettempdir()

    def open_file(self, relative_path, mode='r', encoding=None, **kwargs):
        """
        Abre un archivo de recurso.
        
        Args:
            relative_path (str): Ruta relativa al archivo
            mode (str): Modo de apertura ('r', 'w', 'rb', etc.)
            encoding (str, optional): Codificación del archivo
            **kwargs: Argumentos adicionales para la función open()
            
        Returns:
            file: Objeto archivo abierto
        """
        path = self.get_path(relative_path)
        try:
            return open(path, mode=mode, encoding=encoding, **kwargs)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al abrir {relative_path}: {str(e)}")
            raise
    
    def file_exists(self, relative_path):
        """
        Verifica si un archivo existe.
        
        Args:
            relative_path (str): Ruta relativa al archivo
            
        Returns:
            bool: True si el archivo existe, False en caso contrario
        """
        return os.path.exists(self.get_path(relative_path))
    
    def get_contents(self, dir_path):
        """
        Obtiene el contenido de un directorio.
        
        Args:
            dir_path (str): Ruta relativa al directorio
            
        Returns:
            list: Lista de archivos y directorios
        """
        path = self.get_path(dir_path)
        try:
            return os.listdir(path)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error al listar directorio {dir_path}: {str(e)}")
            return []
    
    def join_paths(self, *paths):
        """
        Une segmentos de ruta de forma segura para el sistema operativo actual.
        
        Args:
            *paths: Segmentos de ruta a unir
            
        Returns:
            str: Ruta unida y normalizada
        """
        return os.path.normpath(os.path.join(*paths))

# Instancia global para uso en toda la aplicación
resource_manager = ResourceManager()