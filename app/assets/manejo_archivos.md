# Pasos manejo de archivos del expediente electrónico (pseudoalgoritmo)

1. Ingresar a la carpeta del expediente electrónico a gestionar que es determinada por el usuario.
2. Validar e individualizar el expediente que se está gestionando (**radicado de 23 dígitos**) para comparar con información de la BD.
3. (prepare_data) Validar estado de la **carpeta**:
   - Verificar si existe índice
      1. Si existe el índice
         1. Verificar que sea accesible
         2. Obtener todos los metadatos relacionados al interior de la hoja de Excel
      2. Si no existe el índice, crearlo
   - Verificar archivos de la carpeta de conformidad con el protocolo
   - Validar accesibilidad a los archivos
   - Validar formato de archivo (pdf, doc, docx, xls, xlsx, entre otros)
   - Verificar acceso a los metadatos
   - Verificar que sea posible contabilizar páginas
   - Validar si existen archivos comprimidos: descomprimirlos y ubicarlos en orden
   - Validar si existen archivos en subcarpetas: si en la subcarpeta hay menos de 10 archivos sacarlos y ubicarlos en la carpeta raiz del expediente
   - Validar consecutivo:
      - Comprobar cantidad de dígitos del consecutivo (01, 001, 0001) permita cambiar la cantidad de digitos cuando se requiera
      - Comprobar que el orden del consecutivo se cumpla, posibles situaciones:
         - El consecutivo está en orden en todos los archivos
         - Faltan consecutivos (001, 002, 003, 007, 008)
         - Faltan archivos por asignar consecutivo
4. (extractor) Validar estado de **archivos e índice**:
   1. Obtener todos los datos del índice y los metadatos de los archivos
      - Para el **índice**:
         - Comparar registros con la información en BD local solo si existen
         - Validar que los archivos y consecutivos cumplan con los registros del libro índice
      - Para los **archivos**:
         - Comparar los datos con la información en BD solo si existen
      - Comparando datos de los archivos y registros del indice pueden suceder las siguientes posibilidades:
         - Los nombres de los archivos en carpeta y los registros del índice coinciden (NOTHING)
         - El índice no está actualizado:
            1. Está sin diligenciar (vacío) (UPDATE)
            2. El índice tiene algunos registros que coinciden con los archivos en carpeta, pero faltan otros por verificar y registrar (Se deben de tener en cuenta las fechas de creación de documento e incorporación al expediente que registre en el índice para almacenar dicha información en la BD) (UPDATE)
         - Los datos del índice relacionan archivos inexistentes en la carpeta (BREAK) (IMPORTANTE: carpeta e índice con  falencias ya que no hay integridad y unicidad de la información)
         - Los datos del índice no están actualizados con los existentes en la carpeta. (UPDATE)
   2. Capturar los nombres y los metadatos de los archivos (almacenar metadatos en BD para hacer comparaciones de  integridad y unicidad), y verificar el cumplimiento de las condiciones del protocolo:
      - Los nombres de los archivos no deben superar los 40 caracteres (eso impedirá el proceso de backup)
      - Al nombrar los archivos no se deberán incluir ni guiones ni espacios, no utilizar caracteres especiales como /#%&:<>().¿?, o tildes
      - Usar mayúscula inicial. Si el nombre es compuesto, usar mayúscula al inicio de cada palabra, ejemplo: FalloTutela
      - Los memoriales (subcarpetas) que consistan en más de 10 archivos deberán ingresarse a una carpeta que se denominará con el siguiente formato "AnexosMemorialAAAAMMDD" (cadena de texto) y se registrará en el índice de expediente electrónico
      - Tener en cuenta cuando un archivo es nombrado con solo números dentro de la carpeta digital
      - Validar la cantidad de ceros del consecutivo
5. (Executer)
