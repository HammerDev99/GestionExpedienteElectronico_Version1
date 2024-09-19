import PyPDF2
import warnings
import sys
from PyPDF2 import PdfReader

def count_pages_in_pdf(pdf_path):
    """
    Cuenta el número de páginas en un archivo PDF utilizando dos métodos diferentes.
    
    :param pdf_path: Ruta del archivo PDF
    :return: Número de páginas en el documento
    """
    # Primer método: PyPDF2.PdfFileReader
    try:
        with open(pdf_path, "rb") as f:
            pdf = PyPDF2.PdfFileReader(f)
            if not sys.warnoptions:
                warnings.simplefilter("ignore")
            return pdf.getNumPages()
    except Exception as e:
        print(f"Error al contar páginas con PyPDF2.PdfFileReader: {e}")

    # Segundo método: PyPDF2.PdfReader
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error al contar páginas con PyPDF2.PdfReader: {e}")
        return 0
    
# Ejemplo de uso
pdf_path = r"app\assets\archivo_firmado_o_protegido.pdf"
total_pages = count_pages_in_pdf(pdf_path)
print(f"El documento tiene {total_pages} páginas.")