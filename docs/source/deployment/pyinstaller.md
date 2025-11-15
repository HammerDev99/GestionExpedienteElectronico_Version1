# Build con PyInstaller

## Introducción

Esta guía cubre el proceso completo de empaquetado de GestionExpedienteElectronico_Version1 usando PyInstaller para crear ejecutables distribuibles en Windows.

## Configuración de PyInstaller

### Instalación de PyInstaller

```bash
# Activar ambiente virtual
.venv\Scripts\Activate  # Windows

# Instalar PyInstaller
pip install pyinstaller==5.13.0
```

!!! note "Versión Específica"
    Se recomienda usar PyInstaller 5.13.0 por compatibilidad verificada con xlwings y pywin32.

### Estructura de Archivos de Spec — Resumen

El archivo `config/main.spec` organiza el empaquetado en cuatro bloques principales:

- Analysis: define el script de entrada, rutas de búsqueda y referencias a binarios/datos/imports. Las listas detalladas (datas, hiddenimports, binaries) han sido omitidas por seguridad y se muestran como marcadores.
- PYZ: empaqueta el código puro en un módulo comprimido — sin cambios sensibles.
- EXE: configura el ejecutable (nombre, modo GUI/console, flags de depuración, icono/version). Valores concretos (p. ej. rutas de icono/version, opciones de signing) están ocultos.
- COLLECT: agrupa los artefactos para el modo --onedir; parámetros de recolección y exclusiones se resumen sin detallar entradas específicas.

Fragmento sanitizado (ejemplo):

```python
# Spec (resumen, valores sensibles redacted)
a = Analysis([str(src_path / '__main__.py')],
                pathex=[...],
                binaries=[...],          # REDACTED
                datas=[...],             # REDACTED
                hiddenimports=[...],     # REDACTED
                excludes=[...],
                cipher=None)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas,
            name='AgilEx_by_Marduk',
            console=False,
            icon='REDACTED',
            version='REDACTED')

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='AgilEx_by_Marduk')
```

Recomendación: mantén listas sensibles fuera del repositorio público (usar variables de entorno o archivos localmente ignorados) y documenta solo la estructura y los puntos de extensión necesarios.

---

!!! success "Build Completado"
    Con esta configuración puedes crear ejecutables robustos y optimizados para distribución.