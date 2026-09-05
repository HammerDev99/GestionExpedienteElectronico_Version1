import os
import sys
import tempfile

import pytest

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from utils.resource_manager import ResourceManager


def test_writable_path_in_development_uses_cwd(tmp_path, monkeypatch):
    """En desarrollo la ruta escribible cuelga del directorio actual."""
    monkeypatch.chdir(tmp_path)
    manager = ResourceManager()
    manager.is_frozen = False

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert os.path.samefile(
        os.path.dirname(result), str(tmp_path)
    )


def test_writable_path_when_frozen_uses_localappdata(monkeypatch, tmp_path):
    """Empaquetado, la ruta escribible cuelga de LOCALAPPDATA\\AgilEx."""
    fake_local = tmp_path / "LocalAppData"
    fake_local.mkdir()
    monkeypatch.setenv("LOCALAPPDATA", str(fake_local))

    manager = ResourceManager()
    manager.is_frozen = True

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert "AgilEx" in result
    assert result.endswith("logs")


def test_writable_path_falls_back_to_temp(monkeypatch, tmp_path):
    """Si el destino no es escribible, cae a la carpeta temporal."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "inexistente"))

    manager = ResourceManager()
    manager.is_frozen = True

    def deny(*args, **kwargs):
        raise PermissionError("acceso denegado")

    monkeypatch.setattr(os, "makedirs", deny)

    result = manager.get_writable_path("logs")

    assert os.path.isdir(result)
    assert os.path.samefile(result, tempfile.gettempdir())


def test_writable_path_without_subdir_returns_base(monkeypatch, tmp_path):
    """Sin subdirectorio devuelve la carpeta base de datos de usuario."""
    fake_local = tmp_path / "LocalAppData"
    fake_local.mkdir()
    monkeypatch.setenv("LOCALAPPDATA", str(fake_local))

    manager = ResourceManager()
    manager.is_frozen = True

    result = manager.get_writable_path()

    assert os.path.isdir(result)
    assert result.endswith("AgilEx")
