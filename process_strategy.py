# Contiene las clases de estrategias de procesamiento de carpetas.

import asyncio
from abc import ABC, abstractmethod
from folder_analyzer import FolderAnalyzer
from file_processor import FileProcessor
import gui_notifier
from gui_notifier import MessageType, DialogType, GUIMessage, GUINotifier


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    def __init__(self, notifier: gui_notifier):
        self.notifier = notifier

    @abstractmethod
    def add_folder(self, processor: FileProcessor):
        pass

    @abstractmethod
    def process(self, processor: FileProcessor):
        pass

    """ # Nuevos métodos que serán trasladados desde Application
    @abstractmethod
    def handle_directory_analysis(self):
        pass

    @abstractmethod
    def gestionar_indices_existentes(self):
        pass

    @abstractmethod
    def confirmar_eliminar_indices(self):
        pass

    @abstractmethod
    def procesar_expedientes(self):
        pass

    @abstractmethod
    def _validar_estructura_expediente(self):
        pass

    @abstractmethod
    def _procesar_cuis(self):
        pass 
    
    def gestionar_indices_existentes(self, folder_selected, analyzer):
        pass """


class SingleCuadernoStrategy(ProcessStrategy):
    """Estrategia para procesar un solo cuaderno sin estructura jerárquica."""

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas."""
        
        # Validar carpeta con obtener rutas

        # Validaciones 

        # Procesamiento de carpetas LUEGO DEBE SER LLAMADO DIRECTAMENTE EN EL MÉTODO process
        self.process(processor)

    def process(self, processor: FileProcessor):
        """Procesa un cuaderno sin estructura jerárquica."""
        asyncio.run(processor.process())

        # Notificar finalización
        self.notifier.notify(GUIMessage("✅ Proceso completado.\n*******************\n\n", MessageType.TEXT))
        self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(
            GUIMessage(
                "Proceso completado exitosamente", MessageType.DIALOG, DialogType.INFO
            )
        )
        self.notifier.notify(GUIMessage((0, 1), MessageType.PROGRESS))

class SingleExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar un expediente con estructura de 4 niveles."""

    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas
        pass

    def process(self, processor: FileProcessor):
        """Procesa un expediente con estructura de 4 niveles."""
        pass


class MultiExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar múltiples expedientes con estructura de 5 niveles."""

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas."""
        pass

    def process(self, processor: FileProcessor):
        """Procesa expedientes con estructura de 5 niveles."""
        pass
