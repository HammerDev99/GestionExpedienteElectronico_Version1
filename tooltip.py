import tkinter as tk
from PIL import Image, ImageTk

class Tooltip:
    def __init__(self, widget, image_path, y_offset=25):
        self.widget = widget
        self.image_path = image_path
        self.y_offset = y_offset
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window or not self.image_path:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25 + self.y_offset

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        image = Image.open(self.image_path)
        photo = ImageTk.PhotoImage(image)
        label = tk.Label(tw, image=photo)
        label.image = photo  # Mantener una referencia para evitar que la imagen sea recolectada por el garbage collector
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None