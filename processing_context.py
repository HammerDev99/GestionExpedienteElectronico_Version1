# Gestiona el procesamiento de carpetas usando la estrategia apropiada.

from file_processor import FileProcessor
from process_strategy import (
    SingleCuadernoStrategy,
    SingleExpedienteStrategy,
    MultiExpedienteStrategy,
)
import logging
from gui_notifier import MessageType, DialogType, GUIMessage, GUINotifier


class ProcessingContext:
    """Gestiona el procesamiento de carpetas usando la estrategia apropiada."""

    def __init__(self, gui_notifier: GUINotifier, logger=None):
        self.notifier = gui_notifier
        self.logger = logger or logging.getLogger("ProcessingContext")
        self._strategies = {
            "1": SingleCuadernoStrategy(self.notifier),
            "2": SingleExpedienteStrategy(self.notifier),
            "3": MultiExpedienteStrategy(self.notifier),
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

        # Agregar texto al widget
        """ self.notifier.notify(
            GUIMessage(
                f"Iniciando procesamiento de: {folder_selected}", MessageType.TEXT
            )
        ) """

        # Actualizar estado
        #self.notifier.notify(GUIMessage("Procesando...", MessageType.STATUS))

        # Inicializar barra de progreso
        #self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))

        # Ejecutar estrategia
        strategy.process(processor)

        # Mostrar diálogo de éxito
        """ self.notifier.notify(
            GUIMessage(
                "Proceso completado exitosamente", MessageType.DIALOG, DialogType.INFO
            )
        ) """

        # Actualizar barra de progreso al completar
        #self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))

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
