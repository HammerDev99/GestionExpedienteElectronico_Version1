# coding=utf-8

import sys
import tkinter as tk
# Detectar entorno y configurar importaciones
if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.view import gui
    from src.model.logger_config import setup_logger
else:
    # Entorno de desarrollo
    from view import gui
    from model.logger_config import setup_logger
    

def main():
    # Configurar el logger
    logger = setup_logger()
    logger.info("Iniciando aplicación...")

    try:
        # Crear ventana principal
        root = tk.Tk()

        # Iniciar GUI pasando el logger como parámetro
        gui.Application(root, logger=logger)

        # Iniciar el loop principal
        root.mainloop()

    except Exception:
        logger.exception("Error crítico en la aplicación")
        sys.exit(1)


if __name__ == "__main__":
    main()
