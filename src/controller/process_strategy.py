# Contiene las clases de estrategias de procesamiento de carpetas.

from abc import ABC, abstractmethod
import logging
import os
import send2trash
import sys

if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.model.folder_analyzer import FolderAnalyzer
    from src.model.file_processor import FileProcessor
    from src.controller import gui_notifier
    from src.controller.gui_notifier import MessageType, DialogType, GUIMessage
else:
    # Entorno de desarrollo
    from model.folder_analyzer import FolderAnalyzer
    from model.file_processor import FileProcessor
    from controller import gui_notifier
    from controller.gui_notifier import MessageType, DialogType, GUIMessage


class ProcessStrategy(ABC):
    """Define la interfaz común para todas las estrategias de procesamiento."""

    def __init__(self, notifier: gui_notifier, logger=None):
        self.notifier = notifier
        self.logger = logger or logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def add_folder(self, processor: FileProcessor):
        # Validaciones previas al procesamiento de carpetas.
        pass

    @abstractmethod
    async def process(self, processor: FileProcessor):
        # Procesa las carpetas seleccionadas.
        pass
    
    @abstractmethod
    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        # Muestra información sobre los CUIs que no cumplen con el formato requerido.
        pass

    @abstractmethod
    def handle_directory_analysis(self):
        # Analiza y procesa la estructura de directorios seleccionada.
        pass

    @abstractmethod
    def gestionar_indices_existentes(self, folder_selected, analyzer):
        # Busca y gestiona índices existentes.
        pass

    @abstractmethod
    def confirmar_eliminar_indices(self, indices):
        # Confirma con el usuario si desea eliminar los índices encontrados.
        pass

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
                    "\n------------------------------------------------------------------\n❕ Índices eliminados:\n", MessageType.TEXT
                )
            )
            try:
                for indice in indices:
                    componentes = indice.split(os.sep)[-4:]
                    ruta_relativa = os.path.join(*componentes)
                    send2trash.send2trash(indice)
                    self.notifier.notify(
                        GUIMessage(f"\n🔹{ruta_relativa}", MessageType.TEXT)
                    )
            except Exception as e:
                self.logger.error(f"Error eliminando índice {indice}: {str(e)}")
            return True
        else:
            self.notifier.notify(
                GUIMessage(f"\n------------------------------------------------------------------\n❕ {mensaje}:\n", MessageType.TEXT)
            )
            for indice in indices:
                componentes = indice.split(os.sep)[-4:]
                ruta_relativa = os.path.join(*componentes)
                self.notifier.notify(
                    GUIMessage(f"\n🔹{ruta_relativa}", MessageType.TEXT)
                )
            return False

    def gestionar_indices_existentes(self, folder_selected, analyzer):
        """
        Busca y gestiona índices existentes.

        Args:
            folder_selected (str): Ruta de la carpeta seleccionada.
            analyzer (FolderAnalyzer): Instancia del analizador de carpetas.

        Returns:
            bool: True si se deben continuar las operaciones, False si se deben detener.
        """
        indices = analyzer.buscar_indices_electronicos(folder_selected)
        if indices:
            indices_eliminados = self.confirmar_eliminar_indices(indices)
            if not indices_eliminados:
                self.notifier.notify(GUIMessage("", MessageType.STATUS))
                return False
        return True

    def _validar_estructura_carpetas(self, estructura_directorios, selected_value):
        """Valida la estructura de carpetas y retorna rutas inválidas"""
        rutas_invalidas = []
        nivel_maximo = self._obtener_nivel_maximo(selected_value)
        
        self._analizar_estructura(
            estructura_directorios, "", 0, nivel_maximo, rutas_invalidas
        )
        
        return rutas_invalidas

    def _obtener_nivel_maximo(self, selected_value):
        """Determina nivel máximo según opción seleccionada."""
        return 2 if selected_value == "2" else 3

    def _analizar_estructura(
        self, directorio, ruta_actual, nivel, nivel_maximo, rutas_invalidas
    ):
        """Analiza recursivamente la estructura buscando carpetas invalidas."""
        if not isinstance(directorio, dict):
            return False

        if nivel >= nivel_maximo:
            self._verificar_subcarpetas(directorio, ruta_actual, rutas_invalidas)
            return False

        for nombre, contenido in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre)
            self._analizar_estructura(
                contenido, nueva_ruta, nivel + 1, nivel_maximo, rutas_invalidas
            )

    def _verificar_subcarpetas(self, directorio, ruta_actual, rutas_invalidas):
        """Verifica si existen subcarpetas en el nivel actual."""
        for nombre, contenido in directorio.items():
            if isinstance(contenido, dict):
                rutas_invalidas.append(os.path.join(ruta_actual, nombre))

    def _validar_estructura_expediente(self, lista_cui, lista_subcarpetas, carpetas_omitidas):
        """Valida que la estructura del expediente sea correcta"""
        if (
            not lista_cui
            and not lista_subcarpetas
            and (not carpetas_omitidas or isinstance(carpetas_omitidas, set))
        ):
            self.notifier.notify(
                GUIMessage(
                    "❌ Error en la estructura de carpetas\n\n"
                    "Se detectaron archivos sueltos donde debería haber unicamente carpetas.\n\n"
                    "📝 Recomendaciones:\n\n"
                    "1. Asegúrese de que sus carpetas siguen exactamente la estructura del protocolo y la opción elegida\n"
                    "2. No incluya archivos en niveles donde debe haber carpetas",
                    MessageType.DIALOG,
                    DialogType.ERROR,
                )
            )
            return False
        return True

    def _mostrar_carpetas_omitidas(self, carpetas_omitidas, directorios_excluidos):
        """Muestra información sobre las carpetas que fueron omitidas por no cumplir con la estructura."""
        try:
            if carpetas_omitidas or directorios_excluidos:
                mensaje_detalle = (
                    "\n------------------------------------------------------------------\n⚠️ Los siguientes elementos no se procesarán debido a problemas en su estructura. Por favor, revise la organización de estas carpetas y archivos:\n\n🔹"
                )
                
                # Combinar y eliminar duplicados
                listas_unidas = list(carpetas_omitidas) + list(directorios_excluidos)
                listas_unidas = sorted(set(listas_unidas))
                
                if listas_unidas:
                    mensaje_detalle += ".\n🔹".join(listas_unidas[:-1])
                    if len(listas_unidas) > 1:
                        mensaje_detalle += ".\n🔹"
                    mensaje_detalle += listas_unidas[-1]
                
                self.logger.warning(f"⚠️ Los siguientes elementos no se procesarán debido a problemas en su estructura: {listas_unidas}")
                self.notifier.notify(
                    GUIMessage(
                        mensaje_detalle,
                        MessageType.TEXT,
                    )
                )
        except Exception as e:
            self.logger.error(
                f"Error al mostrar las carpetas omitidas: {str(e)}",
                exc_info=True,
            )

    # === MÉTODOS COMUNES DE ADD_FOLDER ===
    def _notify_no_folder_selected(self):
        """Notifica que no se ha seleccionado ninguna carpeta."""
        self.notifier.notify(
            GUIMessage(
                "No se ha seleccionado ninguna carpeta.",
                MessageType.DIALOG,
                DialogType.WARNING,
            )
        )

    def _notify_start_processing(self):
        """Notifica el inicio del procesamiento."""
        self.notifier.notify(GUIMessage("\n*******************", MessageType.TEXT))

    def _notify_folder_selected(self, folder_path):
        """Notifica la carpeta seleccionada con formato estándar."""
        self.notifier.notify(
            GUIMessage(
                f"\n------------------------------------------------------------------\n❕ Carpeta seleccionada:\n\n🔹{folder_path}",
                MessageType.TEXT,
            )
        )

    def _notify_ready_to_process(self):
        """Notifica que está listo para procesar."""
        self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("Listo para procesar", MessageType.STATUS))

    def _notify_empty_folder(self):
        """Notifica que la carpeta está vacía o no es accesible."""
        self.notifier.notify(
            GUIMessage(
                "La carpeta seleccionada está vacía o no es accesible.",
                MessageType.DIALOG,
                DialogType.WARNING,
            )
        )

    def _notify_process_stopped(self):
        """Notifica que el procedimiento fue detenido por el usuario."""
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(
            GUIMessage(
                "Procedimiento detenido",
                MessageType.DIALOG,
                DialogType.INFO,
            )
        )

    def _select_and_validate_folder(self):
        """
        Selecciona y valida la carpeta inicial común para todas las estrategias.
        
        Returns:
            str or None: Ruta de la carpeta seleccionada o None si no se seleccionó
        """
        from tkinter import filedialog
        
        folder_selected = os.path.normpath(filedialog.askdirectory())
        if folder_selected in [".", ""]:
            self._notify_no_folder_selected()
            return None
        
        self._notify_start_processing()
        return folder_selected

    # === MÉTODOS COMUNES DE PROCESS() ===
    def _notify_select_folder_to_process(self):
        """Notifica que se debe seleccionar una carpeta para procesar."""
        self.notifier.notify(
            GUIMessage(
                "Seleccione una carpeta para procesar",
                MessageType.DIALOG,
                DialogType.INFO,
            )
        )

    def _get_user_confirmation(self, total_items, item_type, folder_name):
        """
        Obtiene confirmación del usuario para procesar.
        
        Args:
            total_items (int): Número total de elementos a procesar
            item_type (str): Tipo de elemento (archivos, cuadernos, etc.)
            folder_name (str): Nombre de la carpeta
            
        Returns:
            bool: True si el usuario confirma, False si cancela
        """
        return self.notifier.notify(
            GUIMessage(
                f'Se procesarán {total_items} {item_type} que contiene la carpeta '
                f'"{folder_name}". ¿Desea continuar?',
                MessageType.DIALOG,
                DialogType.CONFIRM,
            )
        )

    def _notify_processing_start(self):
        """Notifica el inicio del procesamiento con progreso y mensajes estándar."""
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(GUIMessage((0.1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("\n------------------------------------------------------------------\n🔄 Proceso iniciado...\n\n", MessageType.TEXT))
        self.notifier.force_update()

    def _notify_processing_complete(self):
        """Notifica la finalización exitosa del procesamiento."""
        self.notifier.notify(GUIMessage((1, 1), MessageType.PROGRESS))
        self.notifier.notify(GUIMessage("", MessageType.STATUS))
        self.notifier.notify(
            GUIMessage("\n✅ Proceso completado.\n------------------------------------------------------------------\n*******************\n\n", MessageType.TEXT)
        )
        self.notifier.notify(
            GUIMessage(
                "Proceso completado exitosamente",
                MessageType.DIALOG,
                DialogType.INFO,
            )
        )
        self.notifier.notify(GUIMessage((0, 1), MessageType.PROGRESS))

    def _notify_processing_error(self, error_message):
        """
        Notifica un error durante el procesamiento.
        
        Args:
            error_message (str): Mensaje de error a mostrar
        """
        self.logger.error(f"Error en procesamiento: {error_message}", exc_info=True)
        self.notifier.notify(
            GUIMessage(
                f"Error durante el procesamiento: {error_message}",
                MessageType.DIALOG,
                DialogType.ERROR,
            )
        )

    # === MÉTODOS COMUNES DE HANDLE_DIRECTORY_ANALYSIS ===
    def _validate_and_process_cuis(self, lista_cui, lista_subcarpetas):
        """
        Valida y procesa los CUIs encontrados en la estructura de directorios.
        
        Args:
            lista_cui (list): Lista de CUIs a validar
            lista_subcarpetas (list): Lista de subcarpetas correspondientes
        """
        if lista_cui and lista_subcarpetas:
            cuis_validos = set()
            cuis_invalidos = set()
            
            for cui in lista_cui:
                es_valido, cui_limpio = self._validar_cui(cui)
                if es_valido:
                    cuis_validos.add(cui_limpio)
                else:
                    cuis_invalidos.add(cui)
            
            # Mostrar CUIs inválidos si los hay
            if cuis_invalidos:
                self._mostrar_cuis_invalidos(cuis_invalidos, lista_cui)

    def _show_omitted_folders_if_any(self, carpetas_omitidas, directorios_excluidos):
        """
        Muestra carpetas omitidas y directorios excluidos si existen.
        
        Args:
            carpetas_omitidas (set or list): Carpetas omitidas
            directorios_excluidos (set or list): Directorios excluidos
        """
        if carpetas_omitidas or directorios_excluidos:
            self._mostrar_carpetas_omitidas(carpetas_omitidas or [], directorios_excluidos or [])

    def _show_directory_analysis_complete(self, folder_selected):
        """
        Muestra que el análisis de directorio está completo y listo para procesar.
        
        Args:
            folder_selected (str): Ruta de la carpeta seleccionada
        """
        # Ya tenemos _notify_folder_selected() pero SingleCuaderno necesita progreso adicional
        self._notify_folder_selected(folder_selected)
        # Para SingleCuaderno, agregar progreso y status (las otras estrategias no lo necesitan)

    def _show_directory_analysis_complete_with_progress(self, folder_selected):
        """
        Muestra que el análisis está completo con progreso (específico para SingleCuaderno).
        
        Args:
            folder_selected (str): Ruta de la carpeta seleccionada  
        """
        self._notify_folder_selected(folder_selected)
        self._notify_ready_to_process()

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        """
        Muestra información sobre los CUIs que no cumplen con el formato requerido.
        Implementación común para SingleExpediente y MultiExpediente.
        
        Args:
            cuis_invalidos (set): Conjunto de CUIs inválidos
            lista_cui (list): Lista original de CUIs (no usada en implementación base)
        """
        if cuis_invalidos:
            mensaje = f"\n------------------------------------------------------------------\n❕ Se encontr{'aron' if len(cuis_invalidos) > 1 else 'ó'} radicado{'s' if len(cuis_invalidos) > 1 else ''} (CUI) que no {'cumplen' if len(cuis_invalidos) > 1 else 'cumple'} con los 23 dígitos.\n\n   🔹"
            
            cuis_invalidos_ordenados = sorted(cuis_invalidos)
            if cuis_invalidos_ordenados:
                mensaje += ".\n   🔹".join(cuis_invalidos_ordenados[:-1])
                if len(cuis_invalidos_ordenados) > 1:
                    mensaje += ".\n   🔹"
                mensaje += cuis_invalidos_ordenados[-1]
            
            self.notifier.notify(
                GUIMessage(
                    mensaje,
                    MessageType.TEXT,
                )
            )


class SingleCuadernoStrategy(ProcessStrategy):
    """Estrategia para procesar un solo cuaderno sin estructura jerárquica."""

    def __init__(self, notifier: gui_notifier, logger=None):
        super().__init__(notifier, logger)
        self.folder_selected = None
        self.expediente = None
        self.despacho = ""
        self.subserie = ""
        self.radicado = ""

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas para un solo cuaderno."""
        
        # 1. Selección y validación inicial común
        folder_selected = self._select_and_validate_folder()
        if not folder_selected:
            return False
        
        # 2. Validar que existan archivos en la carpeta seleccionada
        try:
            estructura_directorios = os.listdir(folder_selected)
        except (OSError, PermissionError):
            self._notify_empty_folder()
            return False
            
        if not estructura_directorios:
            self._notify_empty_folder()
            return False

        # 3. Detectar anexos masivos (carpetas dentro de la carpeta seleccionada)
        carpetas = []
        for item in estructura_directorios:
            if os.path.isdir(os.path.join(folder_selected, item)):
                carpetas.append(item)
        
        if len(carpetas) >= 1:
            cadena_rutas_anexos = ""
            for carpeta in carpetas:
                cadena_rutas_anexos += "\n🔹" + carpeta 
            self.notifier.notify(
                GUIMessage(
                    f"\n------------------------------------------------------------------\n❕ Se encontraron anexos masivos en:\n{cadena_rutas_anexos}",
                    MessageType.TEXT,
                )
            )

        # 4. Crear analizador y gestionar índices existentes
        analyzer = FolderAnalyzer({}, None, logger=self.logger)
        continuar = self.gestionar_indices_existentes(folder_selected, analyzer)
        if not continuar:
            return False

        # 5. Guardar datos para procesamiento
        self.folder_selected = folder_selected
        self.expediente = folder_selected

        # 6. Mostrar carpeta seleccionada
        self._notify_folder_selected(folder_selected)

        # 7. Validar CUI si se proporcionó radicado
        if self.radicado or self.radicado == "":
            cui_valido, cui = self._validar_cui(self.radicado)
            if not cui_valido:
                self._mostrar_cuis_invalidos(cui, None)
            else:
                self.radicado = cui

        # 8. Actualizar progressbar y status como las otras estrategias
        self._notify_ready_to_process()

        return True

    async def process(self, processor: FileProcessor):
        """Procesa un cuaderno sin estructura jerárquica."""
        
        if not self.folder_selected:
            self._notify_select_folder_to_process()
            return False

        # 1. Manejar su propia confirmación
        try:
            total_archivos = len(os.listdir(self.folder_selected))
        except (OSError, PermissionError):
            total_archivos = 0
            
        confirm = self._get_user_confirmation(
            total_archivos, 
            "archivos", 
            os.path.basename(self.folder_selected)
        )

        if not confirm:
            self._notify_process_stopped()
            return False

        # 2. Crear FileProcessor con los datos de la estrategia
        processor = FileProcessor(
            self.folder_selected,
            "",
            self.despacho,
            self.subserie,
            self.radicado,
            logger=self.logger,
        )

        # 3. Notificar inicio del procesamiento
        self._notify_processing_start()
        self.notifier.notify(
            GUIMessage(
                "🔹"
                + self.radicado
                + os.path.normpath(os.path.basename(self.folder_selected))
                + "\n",
                MessageType.TEXT,
            )
        )

        # 4. Procesar el cuaderno
        processor._process_excel()

        # 5. Notificar finalización
        self._notify_processing_complete()
        
        return True

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
        self._show_directory_analysis_complete_with_progress(folder_selected)

    def _mostrar_cuis_invalidos(self, cuis_invalidos, lista_cui=None):
        """
        Muestra información sobre los CUIs que no cumplen con el formato requerido.

        Args:
            cuis_invalidos (str): CUI inválido para SingleCuaderno
            lista_cui (list): Lista original de CUIs (no usada en SingleCuaderno)
        """
        if cuis_invalidos or cuis_invalidos == "":
            mensaje = f"\n------------------------------------------------------------------\n❕ Se encontró radicado (CUI) que no cumple con los 23 dígitos."
            
            self.notifier.notify(
                GUIMessage(
                    mensaje,
                    MessageType.TEXT,
                )
            )


class SingleExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar un expediente con estructura de 4 niveles."""

    def __init__(self, notifier: gui_notifier, logger=None):
        super().__init__(notifier, logger)
        self.expediente = None
        self.lista_subcarpetas = []
        self.carpetas_omitidas = set()
        self.analyzer = None
        self.despacho = ""
        self.subserie = ""
        self.folder_selected = None

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas para selected_value == '2'"""
        from tkinter import messagebox
        
        # Selección y validación inicial común
        folder_selected = self._select_and_validate_folder()
        if not folder_selected:
            return False
        
        # Crear una instancia del analizador de carpetas
        analyzer = FolderAnalyzer({}, None, logger=self.logger)
        
        self.expediente = folder_selected
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            self._notify_empty_folder()
            return False

        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        analyzer = FolderAnalyzer(
            estructura_directorios, profundidad_maxima, logger=self.logger
        )

        # Implementación del manejo de anexos masivos para opcion profundidad 4
        rutas_invalidas = self._validar_estructura_carpetas(
            estructura_directorios, "2"
        )
        # Confirmación de carpetas de anexos masivos
        cadena_rutas_anexos = ""
        for i in rutas_invalidas:
            cadena_rutas_anexos += "\n🔹" + i 
        if cadena_rutas_anexos != "":
            self.notifier.notify(
                GUIMessage(
                    f"\n------------------------------------------------------------------\n❕ Se encontraron anexos masivos en:\n{cadena_rutas_anexos}",
                    MessageType.TEXT,
                )
            )

        lista_cui, lista_subcarpetas, carpetas_omitidas, directorios_excluidos = (
            analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 4, "2", folder_selected
            )
        )

        # Verificar si las listas están vacías o tienen valores por defecto de error
        if not self._validar_estructura_expediente(
            lista_cui, lista_subcarpetas, carpetas_omitidas
        ):
            self.notifier.notify(GUIMessage("", MessageType.STATUS))
            return False

        # Llamar al nuevo método para gestionar índices existentes
        continuar = self.gestionar_indices_existentes(folder_selected, analyzer)
        if not continuar:
            return False

        # Guardar referencias para el procesamiento
        self.lista_subcarpetas = lista_subcarpetas
        self.carpetas_omitidas = carpetas_omitidas
        self.analyzer = analyzer

        self.handle_directory_analysis(
            folder_selected,
            estructura_directorios,
            lista_cui,
            lista_subcarpetas,
            carpetas_omitidas,
            analyzer,
            directorios_excluidos
        )

        if not self.lista_subcarpetas:
            self.notifier.notify(GUIMessage("", MessageType.STATUS))
        else:
            self._notify_ready_to_process()
        
        # Retornar True para indicar éxito
        return True

    async def process(self, processor: FileProcessor):
        """Procesa un expediente con estructura de 4 niveles (selected_value == '2')."""
        from tkinter import messagebox
        
        if not self.lista_subcarpetas:
            self._notify_select_folder_to_process()
            return False

        # Obtener datos de entrada almacenados en la estrategia
        despacho = self.despacho
        subserie = self.subserie

        self.logger.info(f"Procesando {len(self.lista_subcarpetas)} expedientes")
        total_carpetas = sum(len(sublista) for sublista in self.lista_subcarpetas)

        # Confirmación con el usuario
        confirm = self._get_user_confirmation(
            total_carpetas,
            "cuadernos",
            os.path.basename(self.expediente)
        )

        if not confirm:
            self._notify_process_stopped()
            return False

        # Iniciar procesamiento
        self._notify_processing_start()

        try:
            processed = 0
            for sublista in self.lista_subcarpetas:
                for ruta in sublista:
                    # Obtener RDO para selected_value == "2"
                    rdo = os.path.normpath(os.path.basename(self.expediente))
                    rdo = self.analyzer._formater_cui(rdo)

                    # Actualizar GUI
                    self.notifier.notify(
                        GUIMessage(
                            "🔹" + os.path.normpath(
                                os.path.basename(self.expediente) + "/" + ruta
                            ) + "\n",
                            MessageType.TEXT,
                        )
                    )
                    self.notifier.force_update()

                    # Procesar expediente
                    carpeta = os.path.normpath(os.path.join(self.expediente, ruta))
                    processor_instance = FileProcessor(
                        carpeta, "", despacho, subserie, rdo, logger=self.logger
                    )

                    # Procesar de forma asíncrona
                    await processor_instance.process()

                    # Actualizar progreso
                    progress_value = 0.1 + (processed / total_carpetas) * 0.9
                    self.notifier.notify(GUIMessage((progress_value, 1), MessageType.PROGRESS))
                    self.notifier.force_update()
                    processed += 1

            # Finalizar procesamiento
            self._notify_processing_complete()

        except Exception as e:
            self._notify_processing_error(str(e))

    def handle_directory_analysis(
        self,
        folder_selected=None,
        estructura_directorios=None,
        lista_cui=None,
        lista_subcarpetas=None,
        carpetas_omitidas=None,
        analyzer=None,
        directorios_excluidos=None,
    ):
        """Analiza y procesa la estructura de directorios seleccionada."""
        # Mostrar carpeta seleccionada
        self._show_directory_analysis_complete(folder_selected)
        
        # Procesar y validar CUIs
        self._validate_and_process_cuis(lista_cui, lista_subcarpetas)
        
        # Mostrar carpetas omitidas y directorios excluidos
        self._show_omitted_folders_if_any(carpetas_omitidas, directorios_excluidos)


class MultiExpedienteStrategy(ProcessStrategy):
    """Estrategia para procesar múltiples expedientes con estructura de 5 niveles."""

    def __init__(self, notifier: gui_notifier, logger=None):
        super().__init__(notifier, logger)
        self.expediente = None
        self.lista_subcarpetas = []
        self.carpetas_omitidas = set()
        self.analyzer = None
        self.despacho = ""
        self.subserie = ""
        self.folder_selected = None

    def add_folder(self, processor: FileProcessor):
        """Validaciones previas al procesamiento de carpetas para selected_value == '3'"""
        
        # Selección y validación inicial común  
        folder_selected = self._select_and_validate_folder()
        if not folder_selected:
            return False
        
        # Crear una instancia del analizador de carpetas
        analyzer = FolderAnalyzer({}, None, logger=self.logger)
        
        self.expediente = folder_selected
        estructura_directorios = analyzer.construir_estructura(folder_selected)
        if not estructura_directorios:
            self._notify_empty_folder()
            return False

        profundidad_maxima = analyzer.obtener_profundidad_maxima(estructura_directorios)
        analyzer = FolderAnalyzer(
            estructura_directorios, profundidad_maxima, logger=self.logger
        )

        # Implementación del manejo de anexos masivos para opcion profundidad 5
        rutas_invalidas = self._validar_estructura_carpetas(
            estructura_directorios, "3"
        )
        # Confirmación de carpetas de anexos masivos
        cadena_rutas_anexos = ""
        for i in rutas_invalidas:
            cadena_rutas_anexos += "\n🔹" + i
        if cadena_rutas_anexos != "":
            self.notifier.notify(
                GUIMessage(
                    f"\n------------------------------------------------------------------\n❕ Se encontraron anexos masivos en:\n{cadena_rutas_anexos}",
                    MessageType.TEXT,
                )
            )

        lista_cui, lista_subcarpetas, carpetas_omitidas, directorios_excluidos = (
            analyzer.obtener_lista_rutas_subcarpetas(
                estructura_directorios, 5, "3", None
            )
        )

        # Verificar si las listas están vacías o tienen valores por defecto de error
        if not self._validar_estructura_expediente(
            lista_cui, lista_subcarpetas, carpetas_omitidas
        ):
            self.notifier.notify(GUIMessage("", MessageType.STATUS))
            return False

        # Llamar al nuevo método para gestionar índices existentes
        continuar = self.gestionar_indices_existentes(folder_selected, analyzer)
        if not continuar:
            return False

        # Guardar referencias para el procesamiento
        self.lista_subcarpetas = lista_subcarpetas
        self.carpetas_omitidas = carpetas_omitidas
        self.analyzer = analyzer

        self.handle_directory_analysis(
            folder_selected,
            estructura_directorios,
            lista_cui,
            lista_subcarpetas,
            carpetas_omitidas,
            analyzer,
            directorios_excluidos
        )

        if not self.lista_subcarpetas:
            self.notifier.notify(GUIMessage("", MessageType.STATUS))
        else:
            self._notify_ready_to_process()
        
        # Retornar True para indicar éxito
        return True

    async def process(self, processor: FileProcessor):
        """Procesa múltiples expedientes con estructura de 5 niveles (selected_value == '3')."""
        
        if not self.lista_subcarpetas:
            self._notify_select_folder_to_process()
            return False

        # Obtener datos de entrada almacenados en la estrategia
        despacho = self.despacho
        subserie = self.subserie

        self.logger.info(f"Procesando {len(self.lista_subcarpetas)} expedientes")
        total_carpetas = sum(len(sublista) for sublista in self.lista_subcarpetas)

        # Confirmación con el usuario
        confirm = self._get_user_confirmation(
            total_carpetas,
            "cuadernos",
            os.path.basename(self.expediente)
        )

        if not confirm:
            self._notify_process_stopped()
            return False

        # Iniciar procesamiento
        self._notify_processing_start()

        try:
            processed = 0
            for sublista in self.lista_subcarpetas:
                for ruta in sublista:
                    # Obtener RDO para selected_value == "3" - usar la ruta directamente
                    rdo = os.path.normpath(ruta)
                    rdo = self.analyzer._formater_cui(rdo)

                    # Actualizar GUI
                    self.notifier.notify(
                        GUIMessage(
                            "🔹" + os.path.normpath(
                                os.path.basename(self.expediente) + "/" + ruta
                            ) + "\n",
                            MessageType.TEXT,
                        )
                    )
                    self.notifier.force_update()

                    # Procesar expediente
                    carpeta = os.path.normpath(os.path.join(self.expediente, ruta))
                    processor_instance = FileProcessor(
                        carpeta, "", despacho, subserie, rdo, logger=self.logger
                    )

                    # Procesar de forma asíncrona
                    await processor_instance.process()

                    # Actualizar progreso
                    progress_value = 0.1 + (processed / total_carpetas) * 0.9
                    self.notifier.notify(GUIMessage((progress_value, 1), MessageType.PROGRESS))
                    self.notifier.force_update()
                    processed += 1

            # Finalizar procesamiento
            self._notify_processing_complete()

        except Exception as e:
            self._notify_processing_error(str(e))

    def handle_directory_analysis(
        self,
        folder_selected=None,
        estructura_directorios=None,
        lista_cui=None,
        lista_subcarpetas=None,
        carpetas_omitidas=None,
        analyzer=None,
        directorios_excluidos=None,
    ):
        """Analiza y procesa la estructura de directorios seleccionada."""
        # Mostrar carpeta seleccionada
        self._show_directory_analysis_complete(folder_selected)
        
        # Procesar y validar CUIs
        self._validate_and_process_cuis(lista_cui, lista_subcarpetas)
        
        # Mostrar carpetas omitidas y directorios excluidos
        self._show_omitted_folders_if_any(carpetas_omitidas, directorios_excluidos)