from abc import ABC, abstractmethod
from typing import Tuple, List, Set
import os
from folder_analyzer import FolderAnalyzer


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    @abstractmethod
    def validate_structure(self, folder_selected: str) -> bool:
        """Valida si la estructura de carpetas es correcta."""
        pass

    @abstractmethod
    def process(
        self, folder_selected: str, analyzer: FolderAnalyzer
    ) -> Tuple[List[str], List[List[str]], Set[str]]:
        """Ejecuta el procesamiento de la carpeta."""
        pass

    @abstractmethod
    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        pass


class SingleCuadernoStrategy(ProcessStrategy):
    """Estrategia para procesar un solo cuaderno sin estructura jerárquica."""

    def validate_structure(self, folder_selected: str) -> bool:
        """Valida que la carpeta contenga solo archivos."""
        try:
            return all(
                os.path.isfile(os.path.join(folder_selected, item))
                for item in os.listdir(folder_selected)
            )
        except Exception:
            return False

    def process(
        self, folder_selected: str, analyzer: FolderAnalyzer
    ) -> Tuple[List[str], List[List[str]], Set[str]]:
        """Procesa una carpeta que contiene solo archivos."""
        if not self.validate_structure(folder_selected):
            return [], [], set()

        cui = os.path.basename(folder_selected)
        subcarpetas = [[folder_selected]]

        return [cui], subcarpetas, set()

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "Carpeta con archivos (sin subcarpetas)"


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

    def process(
        self, folder_selected: str, analyzer: FolderAnalyzer
    ) -> Tuple[List[str], List[List[str]], Set[str]]:
        """Procesa un expediente con estructura de 4 niveles."""
        estructura = analyzer.construir_estructura(folder_selected)
        return analyzer.obtener_lista_rutas_subcarpetas(estructura, 4, folder_selected)

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "RADICADO/01PrimeraInstancia/C01Principal/Archivos"


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

    def process(
        self, folder_selected: str, analyzer: FolderAnalyzer
    ) -> Tuple[List[str], List[List[str]], Set[str]]:
        """Procesa expedientes con estructura de 5 niveles."""
        estructura = analyzer.construir_estructura(folder_selected)
        return analyzer.obtener_lista_rutas_subcarpetas(estructura, 5, None)

    def get_expected_structure(self) -> str:
        """Retorna la descripción de la estructura esperada."""
        return "SERIE_SUBSERIE/RADICADO/01PrimeraInstancia/C01Principal/Archivos"
