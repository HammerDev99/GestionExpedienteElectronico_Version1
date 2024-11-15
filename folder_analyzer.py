import os
import logging

class FolderAnalyzer:
    def __init__(self, estructura_directorios, profundidad_maxima = None, logger=None):
        self.logger = logger or logging.getLogger('FolderAnalyzer')
        self.estructura_directorios = estructura_directorios
        self.profundidad_maxima = profundidad_maxima
        self.todas_las_carpetas = set()
        self.carpetas_procesadas = set()
        self.problemas = []

    # getters y setters para los atributos
    def get_estructura_directorios(self):
        return self.estructura_directorios
    
    def set_estructura_directorios(self, estructura_directorios):
        self.estructura_directorios = estructura_directorios

    def get_profundidad_maxima(self):
        return self.profundidad_maxima
    
    def set_profundidad_maxima(self, profundidad_maxima):
        self.profundidad_maxima = profundidad_maxima

    def get_todas_las_carpetas(self):
        return self.todas_las_carpetas
    
    def set_todas_las_carpetas(self, todas_las_carpetas):
        self.todas_las_carpetas = todas_las_carpetas

    def get_carpetas_procesadas(self):
        return self.carpetas_procesadas
    
    def set_carpetas_procesadas(self, carpetas_procesadas):
        self.carpetas_procesadas = carpetas_procesadas

    def get_problemas(self):
        return self.problemas
    
    def set_problemas(self, problemas):
        self.problemas = problemas

    def obtener_todas_carpetas(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """Obtiene todas las carpetas en un nivel específico."""
        todas_carpetas = set()
        
        if self._es_nivel_objetivo(nivel_actual, nivel_deseado, directorio):
            ruta_normalizada = os.path.normpath(ruta_actual.lstrip('/'))
            todas_carpetas.add(ruta_normalizada)
            return todas_carpetas
        
        if not isinstance(directorio, dict) or not directorio:
            return todas_carpetas
        
        for nombre, subdirectorio in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
            todas_carpetas.update(self.obtener_todas_carpetas(
                subdirectorio,
                nivel_deseado,
                nivel_actual + 1,
                nueva_ruta
            ))
        return todas_carpetas

    def _es_nivel_objetivo(self, nivel_actual, nivel_deseado, directorio):
        """Verifica si el nivel actual es el objetivo y es un directorio válido."""
        return nivel_actual == nivel_deseado and isinstance(directorio, dict) and directorio

    def _validar_instancia(self, directorio, ruta):
        """Valida la estructura de instancia judicial."""
        if not any(key.lower().startswith(("primera", "segunda")) for key in directorio.keys()):
            self.problemas.append(f"Ruta '{ruta}' no contiene carpeta de instancia válida")

    def _validar_anio(self, ruta):
        """Valida que el nombre de la carpeta contenga mínimo 23 digitos al inicio sin espacios"""
        try:
            anio = int(os.path.basename(ruta))
            if not (1900 <= anio <= 2100):  # Rango razonable de años
                raise ValueError
        except ValueError:
            self.problemas.append(f"Ruta '{ruta}' no corresponde a un año válido")

    def _analizar_estructura_nivel(self, directorio, nivel, ruta):
        """Analiza la estructura en un nivel específico."""
        if not isinstance(directorio, dict):
            self.problemas.append(f"Ruta '{ruta}' no es un directorio válido")
            return

        if self.profundidad_maxima == 4 and nivel == 2:
            self._validar_instancia(directorio, ruta)
        elif self.profundidad_maxima == 5 and nivel == 1:
            self._validar_anio(ruta)

    def analizar_estructura(self, directorio=None, nivel=0, ruta=""):
        """Analiza recursivamente la estructura del directorio."""
        if directorio is None:
            directorio = self.estructura_directorios

        self._analizar_estructura_nivel(directorio, nivel, ruta)
        
        if isinstance(directorio, dict):
            for nombre, subdirectorio in directorio.items():
                nueva_ruta = os.path.join(ruta, nombre) if ruta else nombre
                self.analizar_estructura(subdirectorio, nivel + 1, nueva_ruta)

    def procesar_carpetas(self):
        """Identifica las carpetas que cumplen con la estructura esperada."""
        for nombre, subdirectorio in self.estructura_directorios.items():
            if not isinstance(subdirectorio, dict):
                continue
                
            if self.profundidad_maxima == 4:
                self.carpetas_procesadas.add(nombre)
            elif self.profundidad_maxima == 5:
                for subnombre, subsubdirectorio in subdirectorio.items():
                    if isinstance(subsubdirectorio, dict):
                        self.carpetas_procesadas.add(os.path.join(nombre, subnombre))

    def generar_reporte(self):
        """Genera el reporte final del análisis."""
        self.todas_las_carpetas = self.obtener_todas_carpetas(self.estructura_directorios, 2)
        self.procesar_carpetas()
        self.analizar_estructura()
        
        carpetas_omitidas = self.todas_las_carpetas - self.carpetas_procesadas
        
        return {
            "total_carpetas": len(self.todas_las_carpetas),
            "carpetas_procesadas": len(self.carpetas_procesadas),
            "carpetas_omitidas": len(carpetas_omitidas),
            "lista_omitidas": sorted(list(carpetas_omitidas)),
            "problemas_detectados": self.problemas
        }
    
    def obtener_rutas_nivel(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """
        Obtiene las rutas de un nivel específico normalizando los separadores.
        """
        rutas = []
        if nivel_actual == nivel_deseado:
            if ruta_actual:  # Solo normalizar si hay una ruta
                ruta_actual = os.path.normpath(ruta_actual)
            rutas.append(ruta_actual)
        elif isinstance(directorio, dict):
            for nombre, subdirectorio in directorio.items():
                nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
                rutas.extend(self.obtener_rutas_nivel(subdirectorio, nivel_deseado, nivel_actual + 1, nueva_ruta))
        return rutas

    def obtener_todas_carpetas(self, directorio, nivel_deseado, nivel_actual=1, ruta_actual=""):
        """
        Obtiene todas las carpetas existentes en un nivel específico.
        
        Args:
            directorio (dict): Estructura de directorios
            nivel_deseado (int): Nivel de profundidad objetivo
            nivel_actual (int): Nivel actual en la recursión
            ruta_actual (str): Ruta acumulada
        
        Returns:
            set: Conjunto de todas las carpetas en el nivel especificado
        """
        todas_carpetas = set()
        
        if nivel_actual == nivel_deseado:
            if isinstance(directorio, dict) and directorio:
                ruta_normalizada = os.path.normpath(ruta_actual.lstrip('/'))
                todas_carpetas.add(ruta_normalizada)
            return todas_carpetas
            
        if not isinstance(directorio, dict) or not directorio:
            return todas_carpetas
            
        for nombre, subdirectorio in directorio.items():
            nueva_ruta = os.path.join(ruta_actual, nombre) if ruta_actual else nombre
            todas_carpetas.update(self.obtener_todas_carpetas(
                subdirectorio,
                nivel_deseado,
                nivel_actual + 1,
                nueva_ruta
            ))
        
        return todas_carpetas

    def _validar_profundidad(self, profundidad):
        """Valida que la profundidad sea 4 o 5."""
        if profundidad not in [4, 5]:
            raise ValueError("La profundidad máxima debe ser 4 o 5")

    def _normalizar_rutas(self, rutas):
        """Normaliza una lista de rutas."""
        return [os.path.normpath(ruta) for ruta in rutas]

    def _procesar_nivel_dos(self, dir_actual, ruta_base):
        """Procesa las carpetas de nivel 2."""
        ruta_base = os.path.normpath(ruta_base) if ruta_base else ""
        todas_nivel_dos = {
            os.path.normpath(ruta) 
            for ruta in self.obtener_todas_carpetas(dir_actual, 2, 1, ruta_base)
        }
        rutas_nivel_dos = self.obtener_rutas_nivel(dir_actual, 2, 1, ruta_base)
        rutas_nivel_cuatro = self.obtener_rutas_nivel(dir_actual, 4, 1, ruta_base)
        
        return todas_nivel_dos, rutas_nivel_dos, rutas_nivel_cuatro

    def _procesar_directorio_profundidad_4(self, directorio):
        """Procesa directorios con profundidad 4."""
        return [
            (subdirectorio, nombre)
            for nombre, subdirectorio in directorio.items()
        ]

    def _procesar_directorio_profundidad_5(self, directorio):
        """Procesa directorios con profundidad 5."""
        return [
            (subsubdirectorio, os.path.join(nombre, subnombre))
            for nombre, subdirectorio in directorio.items()
            for subnombre, subsubdirectorio in subdirectorio.items()
        ]

    def obtener_lista_rutas_subcarpetas(self, directorio, profundidad_maxima, folder_selected=None):
        """
        Obtiene las listas de CUIs, subcarpetas y carpetas omitidas según la profundidad.
        
        Args:
            directorio (dict): Estructura de directorios
            profundidad_maxima (int): Profundidad máxima (4 o 5)
        
        Returns:
            tuple: (lista_cui, lista_rutas_subcarpetas, carpetas_omitidas)
        """
        try:
            self._validar_profundidad(profundidad_maxima)
            
            lista_rutas_subcarpetas = []
            lista_cui = []
            todas_las_carpetas = set()
            carpetas_procesadas = set()

            # Seleccionar procesamiento según profundidad
            directorios_a_procesar = (
                self._procesar_directorio_profundidad_4(directorio) 
                if profundidad_maxima == 4 
                else self._procesar_directorio_profundidad_5(directorio)
            )

            # Procesar cada directorio
            for dir_actual, ruta_base in directorios_a_procesar:
                todas_nivel_dos, rutas_nivel_dos, rutas_nivel_cuatro = self._procesar_nivel_dos(
                    dir_actual, ruta_base
                )
                
                todas_las_carpetas.update(todas_nivel_dos)
                
                if rutas_nivel_dos:
                    rutas_normalizadas = self._normalizar_rutas(rutas_nivel_dos)
                    lista_rutas_subcarpetas.append(rutas_normalizadas)
                    carpetas_procesadas.update(rutas_normalizadas)
                
                # Validar con opcion 1 con opcion 2 ya es funcional
                if folder_selected:
                    if os.path.basename(folder_selected) not in lista_cui:
                        lista_cui.append(os.path.basename(folder_selected))
                else:
                    cui = self._extraer_cui(ruta_base)
                    if cui and cui not in lista_cui:  # Solo añadir CUIs únicos
                        lista_cui.append(cui)

            return lista_cui, lista_rutas_subcarpetas

        except Exception as e:
            self.logger.error(f"Error al procesar la estructura de directorios: {str(e)}")
            return [], [], set()

    
    def encontrar_cuis_faltantes(self, lista_cui, lista_subcarpetas_internas):
        """
        Encuentra los CUIs que no tienen carpetas internas correspondientes.
        
        Args:
            lista_cui: Lista de CUIs
            lista_subcarpetas_internas: Lista de listas con rutas de carpetas
        
        Returns:
            list: CUIs que no tienen carpetas internas
        """
        # Extraer todos los CUIs de las subcarpetas (antes del primer \\)
        cuis_en_subcarpetas = set()
        for sublista in lista_subcarpetas_internas:
            for ruta in sublista:
                cui = ruta.split('\\')[0]
                cuis_en_subcarpetas.add(cui)
        
        # Encontrar CUIs que no están en las subcarpetas
        cuis_faltantes = [cui for cui in lista_cui if cui not in cuis_en_subcarpetas]
        
        return cuis_faltantes

    def _extraer_cui(self, ruta):
        """Extrae el CUI (radicado) de una ruta."""
        partes = ruta.split('\\')
        return partes[0] if partes else None
    
    def _formater_cui(self, ruta):
        """
        Extrae el CUI (radicado) de una ruta y limpia caracteres no deseados.
        
        Args:
            ruta (str): Ruta completa del archivo
            
        Returns:
            str: CUI limpio (solo dígitos) o None si no hay datos válidos
        """
        try:
            # Obtener la primera parte de la ruta (antes del primer backslash)
            partes = ruta.split('\\')
            if not partes:
                return None

            # Tomar solo la primera parte y eliminar espacios iniciales y finales
            cui = partes[0].strip()

            # Extraer solo los dígitos
            cui_limpio = ''.join(caracter for caracter in cui if caracter.isdigit())

            # Verificar que tengamos al menos un dígito
            return cui_limpio if cui_limpio else None

        except Exception as e:
            self.logger.error(f"Error al extraer CUI: {str(e)}")
            return None

    # Función recursiva para construir el diccionario de estructura de directorios
    def construir_estructura(self, ruta):
        estructura = {}
        for item in os.listdir(ruta):
            item_path = os.path.join(ruta, item)
            if os.path.isdir(item_path):
                estructura[item] = self.construir_estructura(item_path)
            else:
                estructura[item] = None
        return estructura
    
    def obtener_profundidad_maxima(self, directorio, nivel_actual=1):
        if not isinstance(directorio, dict) or not directorio:
            # Si no es un diccionario o está vacío, la profundidad es el nivel actual
            return nivel_actual
        else:
            # Calcula la profundidad recursivamente en cada subdirectorio
            return max(self.obtener_profundidad_maxima(subdirectorio, nivel_actual + 1) for subdirectorio in directorio.values())