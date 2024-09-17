
# Pruebas de caja negra

import unittest

from automatizacionEmpleado import AutomatizacionEmpleado as ae
from automatizacionData import AutomatizacionData as ad

class CajaNegraTest(unittest.TestCase):

    def test_fullFilePath(self):

        test_list = ['004-2022-00023 (Pame-SALIÓ) impugnada.txt']
        test_path = 'C:/Users/Daniel/Downloads/'

        resultado = ae.fullFilePath(ae(), test_list, test_path)

        print(resultado)
        
        self.assertEqual(resultado, ["C:/Users/Daniel/Downloads/004-2022-00023 (Pame-SALIÓ) impugnada.txt"])

    def formatNames_test(self):
        resultado = ad.formatNames("",)
        self.assertEqual(result)
        
if __name__ == '__main__':
    unittest.main()