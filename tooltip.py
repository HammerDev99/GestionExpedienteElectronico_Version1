import tkinter as tk
from PIL import Image, ImageTk


class Tooltip:
    def __init__(self, widget, image_path=None, text=None, y_offset=18):
        self.widget = widget
        self.text = text
        self.image_path = image_path
        self.y_offset = y_offset
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        if self.tooltip_window:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 15
        y += self.widget.winfo_rooty() + 15 + self.y_offset

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        if self.image_path:
            image = Image.open(self.image_path)
            photo = ImageTk.PhotoImage(image)
            label = tk.Label(tw, image=photo)
            label.image = photo  # Mantener una referencia para evitar que la imagen sea recolectada por el garbage collector
        elif self.text:
            tw.wm_geometry(f"+{x}+{y-45}")
            label = tk.Label(
                tw,
                text=self.text,
                background="white",
                relief="solid",
                borderwidth=1,
                font=("Helvetica", 10),
            )
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
