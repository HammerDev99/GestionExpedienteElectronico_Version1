# Responsividad de la GUI durante el procesamiento

> **Fecha:** 2026-09-05
> **Estado:** Mitigación aplicada (opción A). Solución estructural (opción B) pendiente de planificación.
> **Versión afectada:** 1.5.1 y anteriores

## 1. Problema observado

Al procesar una carpeta con múltiples expedientes, la ventana de AgilEx deja de responder: al hacer clic sobre ella, Windows muestra el diálogo *"El programa no responde"* y añade *"(No responde)"* al título, pese a que el procesamiento avanza correctamente y termina bien.

El síntoma es especialmente problemático en el contexto institucional: un funcionario que ve "No responde" asume que la aplicación se colgó y la cierra a la fuerza, interrumpiendo un procesamiento válido.

## 2. Causa raíz

El procesamiento corre en el **mismo hilo que la interfaz gráfica**.

`src/view/application.py` invoca el procesamiento así:

```python
def run_async_process(self, app):
    asyncio.run(app.procesa_expedientes())
```

`asyncio.run()` **bloquea el hilo llamador** hasta que la corrutina termina. Ese hilo es el que ejecuta el bucle de eventos de Tkinter, de modo que mientras dura el procesamiento nadie atiende los mensajes de la ventana. Windows interpreta la falta de respuesta como un cuelgue.

El nombre `run_async_process` sugiere concurrencia, pero `asyncio` no libera el hilo: solo permite intercalar tareas *dentro* del mismo hilo, y únicamente en los puntos `await`. El trabajo pesado real —automatización de Excel vía COM en `file_processor.py`, conteo de páginas de PDF/Word en `metadata_extractor.py`— es síncrono y bloqueante, por lo que nunca cede el control.

**Nota:** `file_processor.py:230` usa `ThreadPoolExecutor` para una parte del trabajo, pero el hilo de la GUI queda igualmente bloqueado esperando su resultado.

## 3. Mitigación aplicada (opción A)

Cambio de bajo riesgo que elimina el síntoma sin alterar la arquitectura.

**3.1 `src/controller/gui_notifier.py` — `ProgressObserver.force_update()`**

Se sustituye `update_idletasks()` por `update()`:

| Método | Comportamiento |
|---|---|
| `update_idletasks()` | Solo redibuja la ventana. La barra de progreso avanza, pero los clics quedan sin atender |
| `update()` | Redibuja **y** procesa la cola de eventos. La ventana responde a clics y a redibujado del sistema |

Se envuelve en `try/except tk.TclError` para el caso de que el usuario cierre la ventana durante el procesamiento.

**3.2 `src/view/application.py` — `run_async_process()`**

El botón "Aceptar" se deshabilita durante el procesamiento, con `try/finally` para garantizar su rehabilitación incluso ante error.

Este cambio **no es opcional**: es consecuencia directa del anterior. Mientras la GUI estaba congelada, un segundo clic en "Aceptar" nunca se atendía. Al procesar la cola de eventos con `update()`, ese clic sí se procesaría y dispararía un **segundo procesamiento simultáneo sobre los mismos archivos**. Aplicar 3.1 sin 3.2 introduce un defecto más grave que el síntoma original.

**Lo que esta mitigación no hace:** no paraleliza nada. El tiempo total de procesamiento es idéntico. La aplicación deja de *parecer* colgada, pero durante las operaciones más largas entre dos llamadas a `force_update()` la ventana sigue sin refrescarse.

## 4. Solución estructural pendiente (opción B)

Mover el procesamiento a un hilo de trabajo separado, dejando el hilo de la GUI libre para atender eventos.

### 4.1 Enfoque

- Ejecutar `procesa_expedientes()` en un `threading.Thread` dedicado.
- Comunicar progreso y mensajes desde el hilo trabajador hacia la GUI mediante una `queue.Queue`.
- En el hilo de la GUI, consumir esa cola con `root.after(100, ...)` de forma periódica.
- **Nunca** invocar métodos de widgets Tkinter desde el hilo trabajador: Tkinter no es thread-safe, y hacerlo produce cuelgues y corrupciones intermitentes muy difíciles de diagnosticar.

### 4.2 Riesgo principal: COM y xlwings

`xlwings` automatiza Excel mediante COM, que tiene reglas estrictas de modelo de apartamento (STA/MTA). Mover ese código a otro hilo **sin inicializar COM en él** produce fallos intermitentes: excepciones `CoInitialize has not been called`, objetos Excel que no responden, o procesos `EXCEL.EXE` huérfanos acumulándose en memoria.

El hilo trabajador debe llamar `pythoncom.CoInitialize()` al comenzar y `pythoncom.CoUninitialize()` al terminar (disponible vía `pywin32`, ya presente en las dependencias del proyecto).

Este riesgo es la razón por la que la opción B **no se implementó junto con la A**: introduce una clase de fallo peor que el síntoma que corrige, y exige su propio ciclo de validación.

### 4.3 Alcance de validación requerido

Una implementación de la opción B no puede considerarse completa sin:

- Las tres estrategias de procesamiento revalidadas de extremo a extremo (cuaderno único, expediente único, múltiples expedientes) contra la salida de la versión 1.5.1.
- Verificación de que no quedan procesos `EXCEL.EXE` huérfanos tras procesar y cerrar la aplicación.
- Prueba con una carpeta de gran volumen (el escenario que originó este hallazgo).
- Comportamiento al cerrar la ventana **durante** el procesamiento: el hilo trabajador debe terminar limpiamente, no quedar huérfano.
- Comportamiento ante error en el hilo trabajador: la excepción debe llegar a la GUI, no perderse silenciosamente.

### 4.4 Consideración de diseño adicional

Con el procesamiento en un hilo separado y la GUI plenamente responsiva, conviene evaluar la incorporación de un botón **Cancelar**, que hoy es imposible de ofrecer porque la interfaz está congelada. Requiere que el hilo trabajador consulte periódicamente un `threading.Event` de cancelación entre expedientes.

## 5. Trazabilidad

| Elemento | Referencia |
|---|---|
| Hallazgo original | Prueba manual de instalación MSI, 2026-09-05, procesando carpeta de múltiples expedientes |
| Archivos de la mitigación A | `src/controller/gui_notifier.py`, `src/view/application.py` |
| Precondición para B | `pywin32` ya está en `requirements.txt` (provee `pythoncom`) |
