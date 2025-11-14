# coding=utf-8

import sys
import tkinter as tk
import umami

# Detectar entorno y configurar importaciones
if getattr(sys, "frozen", False):
    # Entorno de producción
    from src.view import application
    from src.model.logger_config import setup_logger
else:
    # Entorno de desarrollo
    from view import application
    from model.logger_config import setup_logger

# Configuración de Umami Analytics
UMAMI_URL = "https://analytics.sprintjudicial.com"
UMAMI_WEBSITE_ID = "d5b05cbe-bdd4-4db5-bedd-ca13ce87312e"
UMAMI_HOSTNAME = "agilex-desktop.local"
VERSION = "1.5"

# Deshabilitar analytics en modo desarrollo si se desea
# umami.disable()  # Descomentar para deshabilitar en desarrollo
    

def main():
    # Configurar el logger
    logger = setup_logger()
    logger.info("Iniciando aplicación...")

    # Inicializar Umami Analytics
    try:
        umami.set_url_base(UMAMI_URL)
        umami.set_website_id(UMAMI_WEBSITE_ID)
        umami.set_hostname(UMAMI_HOSTNAME)

        # Enviar evento de inicio de aplicación
        umami.new_event(
            event_name='app_start',
            title='Aplicación Iniciada',
            url='/app/start',
            custom_data={'version': VERSION}
        )
        logger.info("Analytics configurado correctamente")
    except Exception as e:
        # No fallar si analytics falla
        logger.warning(f"No se pudo inicializar analytics: {e}")

    try:
        # Crear ventana principal
        root = tk.Tk()

        # Iniciar GUI pasando el logger como parámetro
        application.Application(root, logger=logger)

        # Iniciar el loop principal
        root.mainloop()

    except Exception:
        logger.exception("Error crítico en la aplicación")
        sys.exit(1)


if __name__ == "__main__":
    main()
