# Gestiona el procesamiento de carpetas usando la estrategia apropiada.

import logging
import sys

if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.model.file_processor import FileProcessor
    from src.controller.gui_notifier import GUINotifier
    from src.controller.process_strategy import (
        SingleCuadernoStrategy,
        SingleExpedienteStrategy,
        MultiExpedienteStrategy,
    )
else:
    # Entorno de desarrollo
    from model.file_processor import FileProcessor
    from controller.gui_notifier import GUINotifier
    from controller.process_strategy import (
        SingleCuadernoStrategy,
        SingleExpedienteStrategy,
        MultiExpedienteStrategy,
    )


class ProcessingContext:
    """Gestiona el procesamiento de carpetas usando la estrategia apropiada."""

    def __init__(self, gui_notifier: GUINotifier, logger=None):
        self.notifier = gui_notifier
        self.logger = logger or logging.getLogger("ProcessingContext")
        self._strategies = {
            "1": SingleCuadernoStrategy(self.notifier, self.logger),
            "2": SingleExpedienteStrategy(self.notifier, self.logger),
            "3": MultiExpedienteStrategy(self.notifier, self.logger),
        }
        self.analyzer = None

    def add_folder(self, selected_value: str, processor: FileProcessor):
        # Agrega una carpeta usando la estrategia correspondiente al valor seleccionado.
        strategy = self._strategies.get(selected_value)
        self.logger.info(
            f"Agregando carpeta con estrategia {strategy.__class__.__name__}"
        )

        # Ejecutar estrategia
        strategy.add_folder(processor)

    # Procesa una carpeta usando la estrategia correspondiente al valor seleccionado.
    def process_folder(self, selected_value: str, processor: FileProcessor):
        # Procesa una carpeta usando la estrategia correspondiente al valor seleccionado.
        strategy = self._strategies.get(selected_value)
        self.logger.info(
            f"Procesando carpeta con estrategia {strategy.__class__.__name__}"
        )

        # Ejecutar estrategia
        strategy.process(processor)
