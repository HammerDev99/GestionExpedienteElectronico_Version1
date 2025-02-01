# Aplica el patron Observer para notificar cambios en la GUI.

from abc import ABC, abstractmethod
from enum import Enum
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Union, Tuple


class MessageType(Enum):
    """
    Define los tipos de mensajes soportados por el sistema de observadores.
    Los tipos disponibles son:
        TEXT: Para mensajes de texto en widgets
        PROGRESS: Para actualización de barras de progreso
        DIALOG: Para mostrar diálogos modales
        STATUS: Para actualizar etiquetas de estado
    """
    TEXT = "text"
    PROGRESS = "progress"
    DIALOG = "dialog"
    STATUS = "status"


class DialogType(Enum):
    """
    Define los tipos de diálogos disponibles para mostrar al usuario.
    Los tipos son:
        INFO: Para mensajes informativos
        WARNING: Para advertencias
        ERROR: Para errores
    """
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class GUIMessage:
    """
    @param: content tipo Union[str, Tuple[float, float]]; contenido del mensaje
    @param: message_type tipo MessageType; tipo de mensaje a enviar
    @param: dialog_type tipo DialogType; tipo de diálogo a mostrar (opcional)
    @modules: tkinter
    
    - Encapsula un mensaje para ser procesado por los observadores de la GUI
    - El contenido puede ser texto o una tupla de valores para la barra de progreso
    - Cada mensaje tiene un tipo específico que determina qué observador lo procesará
    """
    def __init__(
        self,
        content: Union[str, Tuple[float, float]],
        message_type: MessageType,
        dialog_type: DialogType = None,
    ):
        self.content = content
        self.type = message_type
        self.dialog_type = dialog_type


class GUIObserver(ABC):
    """
    @param: message_type tipo MessageType; tipo de mensaje que el observador procesará
    @modules: abc
    
    - Clase base abstracta para todos los observadores de la GUI
    - Define la interfaz común que deben implementar todos los observadores
    - Cada observador se especializa en un tipo específico de mensaje
    """
    def __init__(self, message_type: MessageType):
        self.message_type = message_type

    @abstractmethod
    def update(self, message: GUIMessage) -> None:
        pass


class TextWidgetObserver(GUIObserver):
    """
    @param: text_widget tipo tk.Text; widget de texto a actualizar
    @modules: tkinter
    
    - Observador especializado en actualizar widgets de texto
    - Agrega nuevas líneas de texto al final del widget
    - Mantiene el scroll en la última línea agregada
    """
    def __init__(self, text_widget: tk.Text):
        super().__init__(MessageType.TEXT)
        self.text_widget = text_widget

    def update(self, message: GUIMessage) -> None:
        if message.type == self.message_type:
            self.text_widget.insert(tk.END, f"\n{message.content}")
            self.text_widget.see(tk.END)


class ProgressBarObserver(GUIObserver):
    """
    @param: progress_bar tipo ttk.Progressbar; barra de progreso a actualizar
    @modules: tkinter.ttk
    
    - Observador especializado en actualizar barras de progreso
    - Procesa tuplas de (valor, máximo) para actualizar el progreso
    - Maneja errores de formato en los valores recibidos
    """
    def __init__(self, progress_bar: ttk.Progressbar):
        super().__init__(MessageType.PROGRESS)
        self.progress_bar = progress_bar

    def update(self, message: GUIMessage) -> None:
        if message.type == self.message_type:
            try:
                value, maximum = message.content
                self.progress_bar["maximum"] = maximum
                self.progress_bar["value"] = value
            except (ValueError, TypeError) as e:
                print(f"Error actualizando progress bar: {e}")


class DialogObserver(GUIObserver):
    """
    @param: parent_window tipo tk.Tk; ventana padre para los diálogos
    @modules: tkinter.messagebox
    
    - Observador especializado en mostrar diálogos modales
    - Soporta diferentes tipos de diálogos: información, advertencia y error
    - Los diálogos se muestran centrados respecto a la ventana padre
    """
    def __init__(self, parent_window: tk.Tk):
        super().__init__(MessageType.DIALOG)
        self.parent = parent_window

    def update(self, message: GUIMessage) -> None:
        if message.type == self.message_type:
            if message.dialog_type == DialogType.INFO:
                messagebox.showinfo("Información", message.content)
            elif message.dialog_type == DialogType.WARNING:
                messagebox.showwarning("Advertencia", message.content)
            elif message.dialog_type == DialogType.ERROR:
                messagebox.showerror("Error", message.content)


class StatusLabelObserver(GUIObserver):
    """
    @param: status_var tipo tk.StringVar; variable de control para la etiqueta de estado
    @modules: tkinter
    
    - Observador especializado en actualizar etiquetas de estado
    - Actualiza el texto de la etiqueta mediante una variable de control
    - Permite mostrar mensajes de estado en tiempo real
    """
    def __init__(self, status_var: tk.StringVar):
        super().__init__(MessageType.STATUS)
        self.status_var = status_var

    def update(self, message: GUIMessage) -> None:
        if message.type == self.message_type:
            self.status_var.set(message.content)


class GUINotifier:
    """
    @modules: None
    
    - Implementa el patrón Observer para notificar cambios en la GUI
    - Mantiene una lista de observadores registrados
    - Permite adjuntar y desadjuntar observadores dinámicamente
    - Distribuye los mensajes a todos los observadores registrados
    """
    def __init__(self):
        self._observers = []

    def attach(self, observer: GUIObserver):
        """
        @param: observer tipo GUIObserver; observador a registrar
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: GUIObserver):
        """
        @param: observer tipo GUIObserver; observador a eliminar
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, message: GUIMessage):
        """
        @param: message tipo GUIMessage; mensaje a distribuir a los observadores
        """
        for observer in self._observers:
            observer.update(message)