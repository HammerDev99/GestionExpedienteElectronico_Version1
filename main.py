# coding=utf-8

import automatizacionGUI
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

def main():
    try:
        logging.info("Iniciando aplicación...")
        obj = automatizacionGUI()
        obj.__init__()
    except Exception as e:
        logging.error(f"Error en la aplicación: {str(e)}", exc_info=True)
        sys.exit(1)