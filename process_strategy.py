# Contiene las clases de estrategias de procesamiento de carpetas.

from abc import ABC, abstractmethod
from typing import Tuple, List, Set
import os
from folder_analyzer import FolderAnalyzer
from file_processor import FileProcessor
import asyncio
import gui_notifier
from gui_notifier import MessageType, DialogType, GUIMessage, GUINotifier


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    def __init__(self, notifier: gui_notifier):
        self.notifier = notifier

    @abstractmethod
    def process(self, processor: FileProcessor):
        """Ejecuta el procesamiento de la carpeta."""
        pass


class SingleCuadernoStrategy(ProcessStrategy):
    """Estrategia para procesar un solo cuaderno sin estructura jerárquica."""

    def process(self, processor: FileProcessor):
        """Procesa una subcarpeta"""

        # Notificar inicio
        self.notifier.notify(
            GUIMessage(
                "Proceso completado exitosamente", MessageType.DIALOG, DialogType.INFO
            )
        )
        
        # Procesar
        #asyncio.run(processor.process())
        
        # Notificar éxito
        self.notifier.notify(GUIMessage("Proceso completado", MessageType.STATUS))

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

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "Carpeta con archivos (sin subcarpetas)"

    def process_files(
        self, folder_path: str, despacho: str, subserie: str, rdo: str
    ) -> bool:
        # Procesamiento de archivos para un solo cuaderno
        pass

    def validate_cui(self, cui):
        pass

    def validate_structure(self, folder_selected: str) -> bool:
        """Valida que la carpeta contenga solo archivos."""
        try:
            return all(
                os.path.isfile(os.path.join(folder_selected, item))
                for item in os.listdir(folder_selected)
            )
        except Exception:
            return False


class SingleExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar un expediente con estructura de 4 niveles."""

    def validate_structure(self, folder_selected: str) -> bool:
        """Valida que la estructura tenga 4 niveles."""
        try:
            estructura = FolderAnalyzer({}).construir_estructura(folder_selected)
            profundidad = FolderAnalyzer({}).obtener_profundidad_maxima(estructura)
            return profundidad == 4
        except Exception:
            return False

    def process(self, processor: FileProcessor):
        """Procesa un expediente con estructura de 4 niveles."""
        # estructura = analyzer.construir_estructura(folder_selected)
        # return analyzer.obtener_lista_rutas_subcarpetas(estructura, 4, folder_selected)

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "RADICADO/01PrimeraInstancia/C01Principal/Archivos"

    def process_files(
        self, folder_path: str, despacho: str, subserie: str, rdo: str
    ) -> bool:
        # Procesamiento de archivos para un solo cuaderno
        pass


class MultiExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar múltiples expedientes con estructura de 5 niveles."""

    def validate_structure(self, folder_selected: str) -> bool:
        """Valida que la estructura tenga 5 niveles."""
        try:
            estructura = FolderAnalyzer({}).construir_estructura(folder_selected)
            profundidad = FolderAnalyzer({}).obtener_profundidad_maxima(estructura)
            return profundidad == 5
        except Exception:
            return False

    def process(self, processor: FileProcessor):
        """Procesa expedientes con estructura de 5 niveles."""
        # estructura = analyzer.construir_estructura(folder_selected)
        # return analyzer.obtener_lista_rutas_subcarpetas(estructura, 5, None)

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "SERIE_SUBSERIE/RADICADO/01PrimeraInstancia/C01Principal/Archivos"

    def process_files(
        self, folder_path: str, despacho: str, subserie: str, rdo: str
    ) -> bool:
        # Procesamiento de archivos para un solo cuaderno
        pass
