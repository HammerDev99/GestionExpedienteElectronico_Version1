# test_xlwings.py
import xlwings as xw

class TestExcelManipulation:
    def __init__(self, despacho, subserie, rdo, file_path):
        self.despacho = despacho
        self.subserie = subserie
        self.rdo = rdo
        self.file_path = file_path

    def insert_values(self):
        # Abrir el archivo Excel
        wb = xw.Book(self.file_path)
        sheet = wb.sheets.active

        # Insertar los valores en las celdas específicas
        sheet.range("B3").value = self.despacho  # Despacho
        sheet.range("B4").value = self.subserie  # Subserie
        sheet.range("B5").value = self.rdo  # Radicado

        # Guardar y cerrar el archivo
        wb.save()
        wb.close()

if __name__ == "__main__":
    # Valores de prueba
    despacho = "Despacho de Prueba"
    subserie = "Subserie de Prueba"
    rdo = "05088400300320210001000"
    file_path = "C:\\Desarrollo\\Projects\\GestionExpedienteElectronico_Version1\\app\\assets\\000IndiceElectronicoC0 copy.xlsm"

    # Crear una instancia de la clase y ejecutar la función de inserción
    test_excel = TestExcelManipulation(despacho, subserie, rdo, file_path)
    test_excel.insert_values()