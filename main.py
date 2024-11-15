# coding=utf-8

import gui
from logger_config import setup_logger
import sys
import tkinter as tk

def main():
    # Configurar el logger
    logger = setup_logger()
    logger.info("Iniciando aplicación...")

    try:
        # Crear ventana principal
        root = tk.Tk()
        
        # Iniciar GUI pasando el logger como parámetro
        app = gui.Application(root, logger=logger)
        
        # Iniciar el loop principal
        root.mainloop()
        
    except Exception as e:
        logger.exception("Error crítico en la aplicación")
        sys.exit(1)

if __name__ == '__main__':
    main()