# Contiene las clases de estrategias de procesamiento de carpetas.

from abc import ABC, abstractmethod
import logging
import os
import send2trash
from folder_analyzer import FolderAnalyzer
from file_processor import FileProcessor
import gui_notifier
from gui_notifier import MessageType, DialogType, GUIMessage


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    def __init__(self, notifier: gui_notifier, logger=None):
        self.notifier = notifier
        self.logger = logger or logging.getLogger(self.__class__.__name__)

    def _validar_cui(self, cui):
        """
        Valida que el CUI tenga exactamente 23 dígitos sin caracteres especiales.

        Args:
            cui (str): String a validar que puede contener números dispersos,
                    caracteres especiales y letras

        Returns:
            tuple: (bool, str) - (Es válido, CUI limpio)
                    - Es válido: True si se obtuvieron al menos 23 dígitos
                    - CUI limpio: Los primeros 23 dígitos encontrados o la cadena original
                                si no hay suficientes dígitos
        """
        try:
            # Extraer todos los dígitos de la cadena completa
            cui_limpio = "".join(c for c in cui if c.isdigit())

            # Verificar que tenga al menos 23 dígitos
            es_valido = len(cui_limpio) >= 23

            # Retornar los primeros 23 dígitos si hay suficientes,
            # o toda la cadena de dígitos si no hay 23
            return (es_valido, cui_limpio[:23] if es_valido else cui_limpio)

        except Exception as e:
            self.logger.error(f"Error al validar CUI '{cui}': {str(e)}")
            return False, cui

    @abstractmethod
    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas.
        pass

    @abstractmethod
    def process(self, processor: FileProcessor):
        # Procesa las carpetas seleccionadas.
        pass

    @abstractmethod
    def gestionar_indices_existentes(self, folder_selected, analyzer):
        # Busca y gestiona índices existentes.
        pass

    @abstractmethod
    def confirmar_eliminar_indices(self, indices):
        # Confirma con el usuario si desea eliminar los índices encontrados.
        pass

    @abstractmethod
    def handle_directory_analysis(self):
        # Analiza y procesa la estructura de directorios seleccionada.
        pass

    @abstractmethod
    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        # Muestra información sobre los CUIs que no cumplen con el formato requerido.
        pass


class SingleCuadernoStrategy(ProcessStrategy):
    """Estrategia para procesar un solo cuaderno sin estructura jerárquica."""

    def __init__(self, notifier: gui_notifier, logger=None):
        super().__init__(notifier, logger)

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas."""

        # Crear una instancia del analizador de carpetas
        analyzer = FolderAnalyzer({}, None, logger=self.logger)

        # Llamar al nuevo método para gestionar índices existentes
        continuar = self.gestionar_indices_existentes(processor.get_ruta(), analyzer)
        # Detiene ejecución si se encontraron índices y no se eliminaron
        if not continuar:
            return

        # Actualizar archivos en processor
        processor.set_files(None)

        # INDICA LA CARPETA SELECCIONADA EN TEXVIEW Y DEMÁS INTERACCIONES DE LA GUI
        self.handle_directory_analysis(processor.get_ruta())

        # Validar CUI
        cui_valido, cui = self._validar_cui(processor.rdo)
        if not cui_valido:
            self._mostrar_cuis_invalidos(cui, None)
        else:
            # Actualizar CUI en processor
            processor.set_cui(cui)

    def process(self, processor: FileProcessor):
        """Procesa un cuaderno sin estructura jerárquica."""

        # Notifica el inicio del procesamiento
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(GUIMessage((0.1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("\n🔄 Proceso iniciado...\n", MessageType.TEXT))
        self.notifier.notify(
            GUIMessage(
                "- "
                + processor.rdo
                + "/"
                + os.path.normpath(os.path.basename(processor.ruta))
                + "\n",
                MessageType.TEXT,
            )
        )
        self.notifier.force_update()

        # Procesa el cuaderno
        processor._process_excel()

        # Notifica finalización
        self.notifier.notify(
            GUIMessage(
                "✅ Proceso completado.\n*******************\n\n", MessageType.TEXT
            )
        )
        self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(
            GUIMessage(
                "Proceso completado exitosamente",
                MessageType.DIALOG,
                DialogType.INFO,
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

                # self._restablecer_variables_clase()

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
        confirm = self.notifier.notify(
            GUIMessage(
                f"{mensaje}. ¿Desea eliminarlos?",
                MessageType.DIALOG,
                DialogType.CONFIRM,
            )
        )

        if confirm:
            self.notifier.notify(
                GUIMessage(
                    "\n*******************\n✅ Índices eliminados:\n", MessageType.TEXT
                )
            )
            for indice in indices:
                try:
                    componentes = indice.split(os.sep)[-4:]
                    ruta_relativa = os.path.join(*componentes)
                    send2trash.send2trash(indice)
                    self.notifier.notify(
                        GUIMessage(f"   🔹 {ruta_relativa}\n", MessageType.TEXT)
                    )
                except Exception as e:
                    self.logger.error(f"Error eliminando índice {indice}: {str(e)}")
            return True
        else:
            self.notifier.notify(
                GUIMessage(f"\n*******************\n❕ {mensaje}:\n", MessageType.TEXT)
            )
            for indice in indices:
                # Obtener los últimos 4 componentes de la ruta
                componentes = indice.split(os.sep)[-4:]
                ruta_relativa = os.path.join(*componentes)
                self.notifier.notify(
                    GUIMessage(f"   🔹 {ruta_relativa}\n", MessageType.TEXT)
                )
            return False

    def handle_directory_analysis(
        self,
        folder_selected=None,
        estructura_directorios=None,
        lista_cui=None,
        lista_subcarpetas=None,
        carpetas_omitidas=None,
        analyzer=None,
    ):
        """
        Analiza y procesa la estructura de directorios seleccionada.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada
            estructura_directorios (dict): Estructura de directorios
            lista_cui (list): Lista de CUIs
            lista_subcarpetas (list): Lista de subcarpetas
            carpetas_omitidas (set, opcional): Conjunto de carpetas omitidas
            analyzer (FolderAnalyzer, opcional): Instancia del analizador de carpetas
        """

        self.notifier.notify(
            GUIMessage(
                f"\n*******************\n❕ Carpeta seleccionada: {folder_selected}\n",
                MessageType.TEXT,
            )
        )
        self.notifier.notify(GUIMessage("Listo para procesar", MessageType.STATUS))

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        """
        Muestra información sobre los CUIs que no cumplen con el formato requerido.

        Args:
            cuis_invalidos (set): Conjunto de CUIs inválidos
            lista_cui (list): Lista original de CUIs
        """

        if cuis_invalidos or cuis_invalidos == "":
            # self._mensaje(None, "Algunas carpetas no cumplen con el formato requerido de 23 dígitos numéricos.")

            mensaje = f"❕ Se encontr{'aron' if len(cuis_invalidos) > 1 else 'ó'} radicado{'s' if len(cuis_invalidos) > 1 else ''} (CUI) que no {'cumplen' if len(cuis_invalidos) > 1 else 'cumple'} con los 23 dígitos."

            mensaje += cuis_invalidos

            self.notifier.notify(
                GUIMessage(
                    mensaje + "\n",
                    MessageType.TEXT,
                )
            )


class SingleExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar un expediente con estructura de 4 niveles."""

    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas
        pass

    def process(self, processor: FileProcessor):
        # Procesa un expediente con estructura de 4 niveles.
        pass

    def confirmar_eliminar_indices(self, indices):
        # Confirma con el usuario si desea eliminar los índices encontrados
        pass

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        # Busca y gestiona índices existentes
        pass

    def handle_directory_analysis(self):
        # Analiza y procesa la estructura de directorios seleccionada
        pass

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        # Muestra información sobre los CUIs que no cumplen con el formato requerido
        pass


class MultiExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar múltiples expedientes con estructura de 5 niveles."""

    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas.
        pass

    def process(self, processor: FileProcessor):
        # Procesa expedientes con estructura de 5 niveles.
        pass

    def confirmar_eliminar_indices(self, indices):
        # Confirma con el usuario si desea eliminar los índices encontrados
        pass

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        # Busca y gestiona índices existentes
        pass

    def handle_directory_analysis(self):
        # Analiza y procesa la estructura de directorios seleccionada
        pass

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        # Muestra información sobre los CUIs que no cumplen con el formato requerido
        pass
