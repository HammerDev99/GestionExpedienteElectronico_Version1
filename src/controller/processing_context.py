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

    def add_folder(self, selected_value: str, processor: FileProcessor, despacho=None, subserie=None, radicado=None):
        # Agrega una carpeta usando la estrategia correspondiente al valor seleccionado.
        strategy = self._strategies.get(selected_value)
        self.logger.info(
            f"Agregando carpeta con estrategia {strategy.__class__.__name__}"
        )

        # Inyectar datos del formulario en todas las estrategias
        strategy.despacho = despacho
        strategy.subserie = subserie
        
        # Para selected_value "1", agregar el radicado
        if selected_value == "1":
            strategy.radicado = radicado

        # Ejecutar estrategia - Todas manejan su propio askdirectory()
        result = strategy.add_folder(processor)
        
        # Para selected_value "1", retornar resultado simple
        if selected_value == "1":
            return result
        
        # Para selected_value "2" y "3", retornar los datos de la estrategia
        if selected_value in ["2", "3"] and hasattr(strategy, 'lista_subcarpetas'):
            return {
                'expediente': strategy.expediente,
                'lista_subcarpetas': strategy.lista_subcarpetas,
                'carpetas_omitidas': strategy.carpetas_omitidas,
                'analyzer': strategy.analyzer,
                'profundidad': 4 if selected_value == "2" else 5
            }
        
        return result

    # Procesa una carpeta usando la estrategia correspondiente al valor seleccionado.
    async def process_folder(self, selected_value: str, processor: FileProcessor):
        # Procesa una carpeta usando la estrategia correspondiente al valor seleccionado.
        strategy = self._strategies.get(selected_value)
        self.logger.info(
            f"Procesando carpeta con estrategia {strategy.__class__.__name__}"
        )

        try:
            # Ejecutar estrategia
            await strategy.process(processor)
        finally:
            # Limpiar la estrategia después del procesamiento (solo para selected_value "2" y "3")
            if selected_value in ["2", "3"] and hasattr(strategy, 'cleanup'):
                strategy.cleanup()
