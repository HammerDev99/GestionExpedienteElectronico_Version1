"""El repositorio es público: no debe exponer datos del cargo ni de la infraestructura de la entidad.

AgilEx es una obra personal publicada bajo MIT; las versiones firmadas por la entidad
se distribuyen por el canal institucional y su documentación interna no vive aquí.
"""
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
THIS_FILE = Path(__file__).resolve()

FORBIDDEN = [
    ("correo institucional", re.compile(r"@cendoj", re.I)),
    ("SharePoint institucional", re.compile(r"sharepoint\.com", re.I)),
    ("Key Vault de la entidad", re.compile(r"kv-csj", re.I)),
    ("incidente de seguridad interno", re.compile(r"804977|RJ-MDE")),
    ("municipio del cargo", re.compile(r"\bbello\b", re.I)),
    ("dependencia de la entidad", re.compile(r"\bCENDOJ\b|\bUTDI", re.I)),
    ("reclamo institucional", re.compile(
        r"desarrollado para el \**Consejo Superior|SOC Rama Judicial|ante el SOC|logo institucional", re.I)),
]

BINARY_SUFFIXES = {".png", ".ico", ".webp", ".xlsm", ".jpg", ".jpeg", ".gif", ".pdf", ".rar", ".zip", ".exe", ".msi"}


def tracked_files():
    out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
    return [name for name in out.decode("utf-8").split("\0") if name]


def tracked_text(name):
    path = ROOT / name
    if path.resolve() == THIS_FILE or path.suffix.lower() in BINARY_SUFFIXES or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


@pytest.mark.parametrize("label,pattern", FORBIDDEN, ids=[label for label, _ in FORBIDDEN])
def test_tracked_files_do_not_expose(label, pattern):
    hits = [name for name in tracked_files() if pattern.search(name)]
    for name in tracked_files():
        for number, line in enumerate(tracked_text(name).splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{name}:{number}")
    assert not hits, f"{label}: {hits[:10]}"
