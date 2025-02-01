from abc import ABC, abstractmethod
from enum import Enum
import tkinter as tk
from typing import List, Optional, Dict

# 1. Definición de tipos de mensajes y eventos
class MessageType(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    PROGRESS = "PROGRESS"

class GUIMessage:
    """Encapsula la información de un mensaje para la GUI"""
    def __init__(self, content: str, message_type: MessageType, show_dialog: bool = False):
        self.content = content
        self.type = message_type
        self.show_dialog = show_dialog
        self.timestamp = None  # Opcional: para ordenar mensajes

# 2. Interfaz Observer
class GUIObserver(ABC):
    """Interfaz base para observadores de la GUI"""
    @abstractmethod
    def update(self, message: GUIMessage) -> None:
        pass

# 3. Implementación concreta de observadores
class TextWidgetObserver(GUIObserver):
    """Observador para el widget de texto"""
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
        self._message_prefixes = {
            MessageType.INFO: "ℹ️ ",
            MessageType.WARNING: "⚠️ ",
            MessageType.ERROR: "❌ ",
            MessageType.SUCCESS: "✅ ",
            MessageType.PROGRESS: "🔄 "
        }

    def update(self, message: GUIMessage) -> None:
        prefix = self._message_prefixes.get(message.type, "")
        self.text_widget.insert(tk.END, f"\n{prefix}{message.content}")
        self.text_widget.see(tk.END)

class ProgressBarObserver(GUIObserver):
    """Observador para la barra de progreso"""
    def __init__(self, progress_var: tk.StringVar):
        self.progress_var = progress_var

    def update(self, message: GUIMessage) -> None:
        if message.type == MessageType.PROGRESS:
            self.progress_var.set(message.content)
        elif message.type == MessageType.SUCCESS:
            self.progress_var.set("")  # Limpiar al completar

class DialogObserver(GUIObserver):
    """Observador para diálogos emergentes"""
    def __init__(self, parent_window: tk.Tk):
        self.parent = parent_window

    def update(self, message: GUIMessage) -> None:
        if message.show_dialog:
            tk.messagebox.showinfo("Mensaje", message.content)

# 4. Sujeto Observable (Subject)
class GUINotifier:
    """Gestiona las notificaciones de la GUI"""
    def __init__(self):
        self._observers: Dict[MessageType, List[GUIObserver]] = {
            message_type: [] for message_type in MessageType
        }

    def attach(self, observer: GUIObserver, message_types: List[MessageType] = None):
        """Registra un observador para tipos específicos de mensajes"""
        types_to_attach = message_types if message_types else list(MessageType)
        for message_type in types_to_attach:
            if observer not in self._observers[message_type]:
                self._observers[message_type].append(observer)

    def detach(self, observer: GUIObserver, message_types: List[MessageType] = None):
        """Elimina un observador de tipos específicos de mensajes"""
        types_to_detach = message_types if message_types else list(MessageType)
        for message_type in types_to_detach:
            if observer in self._observers[message_type]:
                self._observers[message_type].remove(observer)

    def notify(self, message: GUIMessage):
        """Notifica a los observadores registrados para el tipo de mensaje"""
        for observer in self._observers[message.type]:
            observer.update(message)

# 5. Clase ProcessingContext mejorada
class ProcessingContext:
    def __init__(self, gui_notifier: GUINotifier, logger=None):
        self.notifier = gui_notifier
        self.logger = logger

    def notify_process_start(self, folder_selected: str):
        """Notifica el inicio del procesamiento"""
        self.notifier.notify(GUIMessage(
            f"Iniciando procesamiento de: {folder_selected}",
            MessageType.INFO
        ))
        self.notifier.notify(GUIMessage(
            "Procesando...",
            MessageType.PROGRESS
        ))

    def notify_process_success(self):
        """Notifica el éxito del procesamiento"""
        self.notifier.notify(GUIMessage(
            "Proceso completado exitosamente",
            MessageType.SUCCESS,
            show_dialog=True
        ))

    def notify_process_error(self, error_message: str):
        """Notifica un error en el procesamiento"""
        self.notifier.notify(GUIMessage(
            f"Error: {error_message}",
            MessageType.ERROR,
            show_dialog=True
        ))
        self.logger.error(error_message)

# 6. Ejemplo de uso en la clase Application
class Application(tk.Frame):
    def __init__(self, root, logger=None):
        super().__init__(root)
        self.logger = logger
        
        # Inicializar componentes GUI
        self.text_widget = tk.Text(self)
        self.progress_var = tk.StringVar()
        
        # Configurar el sistema de notificación
        self.gui_notifier = GUINotifier()
        
        # Crear y registrar observadores
        text_observer = TextWidgetObserver(self.text_widget)
        progress_observer = ProgressBarObserver(self.progress_var)
        dialog_observer = DialogObserver(root)
        
        # Registrar observadores para tipos específicos
        self.gui_notifier.attach(text_observer)
        self.gui_notifier.attach(progress_observer, [MessageType.PROGRESS])
        self.gui_notifier.attach(dialog_observer)
        
        # Crear ProcessingContext con el notificador
        self.processing_context = ProcessingContext(self.gui_notifier, self.logger)
