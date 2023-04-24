""" Esta clase contiene la lógica para manejar los datos en el archivo de Excel """

class Indice():

    def __init__(self):
        pass

    # ________________________ código refactorizado ⬆️ (Pendiente ⬇️)

    def copyXlsm(self, rutaFinal):
        """ 
        @param: rutaFinal tipo string; contiene ruta expediente
        @modules: os, shutil
        """

        ruta = os.path.dirname(os.path.abspath(__file__)) + r"\assets\000IndiceElectronicoC0.xlsm"
        shutil.copy(ruta, rutaFinal) 
        self.indice = os.path.join(rutaFinal, '000IndiceElectronicoC0.xlsm')

    def createXlsm(self, df, macro_vba, sheet):
        """ 
        @param: df; contiene DataFrame con datos a registrar en excel
        @return: 
        @modules: xlwings

        - Agrega nueva columna al df, ejecuta macro tantas veces como filas tenga el df, Ingresa 
        registros en el xlsm, Guarda el archivo
        - Obtener la fecha actual para registrar en columna 2 (fecha incorporacion expediente)
        - Agregar columna observaciones
        - Optimizar ejecución de la Macro / Insertar fila con xlwings
        """
        
        dfcopy = df.iloc[:,1]
        df.insert(loc=2, column='Fecham', value=dfcopy)
        columnas = ['A', 'B', 'C', 'D', 'E', 'H', 'I', 'J', 'K']
        filaInicial = 12
        #filaFinal = filaInicial + df.shape[0]
        contFila = filaInicial
        for x in range(df.shape[0]):
            macro_vba()
        for i in range(df.shape[0]):
            for j in range(len(columnas)):
                sheet.range(columnas[j]+str(contFila)).value = df.iloc[i,j]
            contFila = contFila + 1

    # Funciones futuras

    def read_xlsm():
        pass

    def update_xlsm():
        pass

    def delete_xlsm():
        pass
