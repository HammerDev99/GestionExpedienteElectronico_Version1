import logging
import os
import sys

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from model.logger_config import setup_logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Evita que los handlers se acumulen entre tests."""
    yield
    logger = logging.getLogger("GestionExpediente")
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)


def test_setup_logger_returns_logger(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    assert logger.name == "GestionExpediente"


def test_setup_logger_writes_file_in_writable_dir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    logger = setup_logger()
    logger.info("mensaje de prueba")

    file_handlers = [
        h for h in logger.handlers if isinstance(h, logging.FileHandler)
    ]
    assert len(file_handlers) == 1
    assert os.path.exists(file_handlers[0].baseFilename)


def test_setup_logger_survives_unwritable_location(monkeypatch):
    """Regresion: no debe lanzar excepcion si no puede crear el archivo.

    Este es el fallo que impedia arrancar desde Program Files.
    """
    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(logging, "FileHandler", deny)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
    stream_handlers = [
        h for h in logger.handlers if isinstance(h, logging.StreamHandler)
    ]
    assert len(stream_handlers) >= 1


def test_setup_logger_never_raises_on_makedirs_failure(monkeypatch):
    """Regresion: os.makedirs fallando no debe propagar excepcion."""
    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(os, "makedirs", deny)

    logger = setup_logger()

    assert isinstance(logger, logging.Logger)
