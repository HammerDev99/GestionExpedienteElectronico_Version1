import win32com.client as win32

def count_pages_in_docx(docx_path):
    # Inicia Microsoft Word
    word = win32.Dispatch("Word.Application")
    word.Visible = False  # No mostrar la ventana de Word
    
    # Abre el documento .docx
    doc = word.Documents.Open(docx_path)
    
    # Recalcula las páginas
    doc.Repaginate()  # Asegura que las páginas se recalculen si es necesario
    
    # Obtiene el número de páginas
    pages = doc.ComputeStatistics(2)  # 2 es el código para contar páginas (wdStatisticPages)

    # Cierra el documento y Word
    doc.Close(False)  # False para no guardar cambios
    word.Quit()

    return pages

def test_page_counter_pywin32():
    docx_path = r"C:\Desarrollo\Projects\GestionExpedienteElectronico_Version1\app\assets\test_document.docx"
    total_pages = count_pages_in_docx(docx_path)
    print(f"El documento tiene {total_pages} páginas.")

if __name__ == "__main__":
    test_page_counter_pywin32()
