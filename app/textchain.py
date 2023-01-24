import os

class textchain:
    def __init__(self, texto=None, cantidad=40):
        self.texto = texto

    def separar(self, texto):
        self.nombre = os.path.splitext(self.texto)[0]
        self.extension = os.path.splitext(self.texto)[1]

    def mayuscula(self, texto):
        self.texto = self.texto.title()

    def 