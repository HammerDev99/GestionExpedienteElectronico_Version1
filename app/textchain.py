import os

""" Con la clase textchain se inicia el proceso de refactorizacion del metodo formatNames() """

class textchain:
    texto = ""
    nombre = ""
    extension = ""

    def __init__(self, texto=None):
        self.texto = texto

    def separar(self):
        self.nombre = os.path.splitext(self.texto)[0]
        self.extension = os.path.splitext(self.texto)[1]

    def mayuscula(self):
        return self.nombre.title()

if __name__ == '__main__':
    cadena = textchain('hola Mundo.txt')
    cadena.separar()
    print(cadena.nombre)
    print(cadena.extension)
    print(cadena.mayuscula())