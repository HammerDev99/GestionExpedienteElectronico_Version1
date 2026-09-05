from datetime import datetime
import logging
import os
import sys

if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.utils.resource_manager import resource_manager
else:
    # Entorno de desarrollo
    from utils.resource_manager import resource_manager


def setup_logger():
    """
    Configura el logger principal de la aplicacion.

    El logging nunca debe impedir que la aplicacion arranque: si el
    destino de archivo no es escribible, el logger queda operativo
    solo con salida por consola.
    """
    logger = logging.getLogger("GestionExpediente")
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    try:
        log_dir = resource_manager.get_writable_path("logs")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"app_{timestamp}.log")

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Logging a archivo deshabilitado: {e}")

    return logger
