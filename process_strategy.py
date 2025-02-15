# Contiene las clases de estrategias de procesamiento de carpetas.

import asyncio
from abc import ABC, abstractmethod
import logging
import os

import send2trash
import file_processor
from folder_analyzer import FolderAnalyzer
from file_processor import FileProcessor
import gui_notifier
from gui_notifier import MessageType, DialogType, GUIMessage, GUINotifier


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    def __init__(self, notifier: gui_notifier, logger=None):
        self.notifier = notifier
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def add_folder(self, processor: FileProcessor):
        pass

    @abstractmethod
    def process(self, processor: FileProcessor):
        pass

    @abstractmethod
    def gestionar_indices_existentes(self, folder_selected, analyzer):
        """
        Busca y gestiona índices existentes.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada.
            analyzer (FolderAnalyzer): Instancia del analizador de carpetas.

        Returns:
            bool: True si se deben continuar las operaciones, False si se deben detener.
        """
        pass

    @abstractmethod
    def confirmar_eliminar_indices(self, indices):
        """
        Confirma con el usuario si desea eliminar los índices encontrados.
        """
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

    def __init__(self, notifier: gui_notifier, logger=None):
        super().__init__(notifier, logger)

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas."""
        
        #******************* Obtener rutas



        # Crear una instancia del analizador de carpetas
        analyzer = FolderAnalyzer({}, None, logger=self.logger)
        # Llamar al nuevo método para gestionar índices existentes
        continuar = self.gestionar_indices_existentes(processor.get_ruta(), analyzer)

        # PENDIENTE INDICAR LA CARPETA SELECCIONADA EN TEXVIEW Y DEMÁS INTERACCIONES DE LA GUI

        # ACTUALIZAR LISTADO DE ARCHIVOS EN PROCESSOR

        # MODIFICAR MENSAJE DE INICIO DE PROCESAMIENTO EN EL SENTIDO DE INDICAR NO UNA CANTIDAD DE CARPETAS SINO DE ARCHIVOS O EL NOMBRE DE LA SUBCARPETA A PROCESAR (Se procesarán 0 carpetas)

        #if not continuar:
        #    return  # Detiene ejecución si se encontraron índices y no se eliminaron

        

        # ******************* Validaciones 

    def process(self, processor: FileProcessor):
        """Procesa un cuaderno sin estructura jerárquica."""
        processor._process_excel()

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
                
                #self._restablecer_variables_clase()
                
                self.notifier.notify(GUIMessage("", MessageType.STATUS))
                return False  # Detiene ejecución si se encontraron índices y no se eliminaron
        return (
            True  # Continúa ejecución si no se encontraron índices o si se eliminaron
        )

    def confirmar_eliminar_indices(self, indices):
        """
        Confirma con el usuario si desea eliminar los índices encontrados.
        """

        cantidad = len(indices)
        mensaje = f"Se encontr{'aron' if cantidad > 1 else 'ó'} {cantidad} índice{'s' if cantidad > 1 else ''} electrónico{'s' if cantidad > 1 else ''} que impide el procesamiento"
        confirm = self.notifier.notify(GUIMessage(
            f"{mensaje}. ¿Desea eliminarlos?",
            MessageType.DIALOG,
            DialogType.CONFIRM
        ))

        # AQUI VOY

        if confirm:
            self.notifier.notify(GUIMessage("\n*******************\n✅ Índices eliminados:\n", MessageType.TEXT))
            for indice in indices:
                try:
                    componentes = indice.split(os.sep)[-4:]
                    ruta_relativa = os.path.join(*componentes)
                    send2trash.send2trash(indice)
                    self.notifier.notify(GUIMessage(f"   🔹 {ruta_relativa}\n", MessageType.TEXT))
                except Exception as e:
                    self.logger.error(f"Error eliminando índice {indice}: {str(e)}")
            return True
        else:
            self.notifier.notify(GUIMessage(f"\n*******************\n❕ {mensaje}:\n", MessageType.TEXT))
            for indice in indices:
                # Obtener los últimos 4 componentes de la ruta
                componentes = indice.split(os.sep)[-4:]
                ruta_relativa = os.path.join(*componentes)
                self.notifier.notify(GUIMessage(f"   🔹 {ruta_relativa}\n", MessageType.TEXT))
            return False

class SingleExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar un expediente con estructura de 4 niveles."""

    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas
        pass

    def process(self, processor: FileProcessor):
        """Procesa un expediente con estructura de 4 niveles."""
        pass

    def confirmar_eliminar_indices(self, indices):
        pass

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        pass


class MultiExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar múltiples expedientes con estructura de 5 niveles."""

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas."""
        pass

    def process(self, processor: FileProcessor):
        """Procesa expedientes con estructura de 5 niveles."""
        pass

    def confirmar_eliminar_indices(self, indices):
        pass

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        pass