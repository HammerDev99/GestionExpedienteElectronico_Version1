import tkinter as tk
from folder_analyzer import FolderAnalyzer
from file_processor import FileProcessor
from process_strategy import (
    SingleCuadernoStrategy,
    SingleExpedienteStrategy,
    MultiExpedienteStrategy,
)
import logging
from typing import List, Set
import os


class ProcessingContext:
    """Gestiona el procesamiento de carpetas usando la estrategia apropiada."""

    def __init__(self, gui_instance, logger=None):
        self.gui = gui_instance
        self.logger = logger or logging.getLogger("ProcessingContext")
        self._strategies = {
            "1": SingleCuadernoStrategy(),
            "2": SingleExpedienteStrategy(),
            "3": MultiExpedienteStrategy(),
        }
        self.analyzer = None

        # Procesa una carpeta usando la estrategia correspondiente al valor seleccionado.

    def process_folder(
        self, folder_selected: str, selected_value: str, processor: FileProcessor
    ):
        strategy = self._strategies.get(selected_value)
        self.logger.info(
            f"Procesando carpeta con estrategia {strategy.__class__.__name__}"
        )

        # Procesar archivo
        folder_selected = self.gui._get_bundled_path(
            os.path.normpath(
                os.path.join(folder_selected, os.path.normpath(folder_selected))
            )
        )

        # Se ejecuta la estrategia según el valor seleccionado
        strategy.process(processor)

        # self.analyzer = FolderAnalyzer({})
        # structure_valid = strategy.validate_structure(folder_selected)

        # if not structure_valid:
        #    return self.handle_invalid_structure(strategy)

    """ # Nuevos métodos trasladados desde Application
    def handle_directory_analysis(self):
        pass

    def gestionar_indices_existentes(self):
        pass

    def confirmar_eliminar_indices(self):
        pass

    def procesar_expedientes(self):
        pass

    def handle_directory_analysis(
        self,
        folder_selected: str,
        estructura_directorios: dict,
        lista_cui: List[str],
        lista_subcarpetas: List[str],
        carpetas_omitidas: Set[str],
    ):
        pass

    def _validar_estructura_expediente(
        self,
        lista_cui: List[str],
        lista_subcarpetas: List[str],
        carpetas_omitidas: Set[str],
    ):
        pass

    def _procesar_cuis(
        self, lista_cui: List[str], lista_subcarpetas: List[str]
    ):
        pass """
