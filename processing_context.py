import tkinter as tk
from folder_analyzer import FolderAnalyzer
from process_strategy import (
    SingleCuadernoStrategy,
    SingleExpedienteStrategy,
    MultiExpedienteStrategy,
)


class ProcessingContext:
    """Gestiona el procesamiento de carpetas usando la estrategia apropiada."""

    def __init__(self, gui_instance):
        self.gui = gui_instance
        self._strategies = {
            "1": SingleCuadernoStrategy(),
            "2": SingleExpedienteStrategy(),
            "3": MultiExpedienteStrategy(),
        }

    def process_folder(self, folder_selected: str, selected_value: str) -> None:
        """Procesa una carpeta usando la estrategia correspondiente al valor seleccionado."""
        strategy = self._strategies.get(selected_value)
        if not strategy:
            tk.messagebox.showerror("Error", "Opción de procesamiento no válida")
            return

        analyzer = FolderAnalyzer({})
        if not strategy.validate_structure(folder_selected):
            tk.messagebox.showwarning(
                "Advertencia",
                f"La estructura no coincide con el formato esperado:\n\n"
                f"{strategy.get_expected_structure()}",
            )
            return

        lista_cui, lista_subcarpetas, carpetas_omitidas = strategy.process(
            folder_selected, analyzer
        )

        if lista_subcarpetas:
            self.gui.handle_directory_analysis(
                folder_selected,
                analyzer.construir_estructura(folder_selected),
                lista_cui,
                lista_subcarpetas,
                carpetas_omitidas,
                analyzer,
            )
