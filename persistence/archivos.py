import json
import os
from pathlib import Path

 #Administra la lectura y escritura de los datos en los archivos JSON
class Archivos:
     #Inicializa la carpeta donde se almacenan los archivos
    def __init__(self, carpeta):
        self.carpeta = Path(carpeta)
        self.carpeta.mkdir(parents=True, exist_ok=True)

      #Lee un archivo JSON y devuelve sus datos
    def leer(self, nombre, inicial):
        ruta = self.carpeta / nombre

        # Si el archivo no existe, se crea con los datos iniciales.
        if not ruta.exists():
            self.guardar(nombre, inicial)

        try:
            return json.loads(ruta.read_text(encoding="utf-8"))
        except (ValueError, OSError) as error:
            raise ValueError(
                f"No se pudo leer {ruta}. "
                f"Conserva el archivo y revisa su JSON."
            ) from error

        #Guarda los datos en un archivo JSON
    def guardar(self, nombre, datos):
        ruta = self.carpeta / nombre
        temporal = ruta.with_suffix(".tmp")

        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=2)
            archivo.flush()
            os.fsync(archivo.fileno())

        temporal.replace(ruta)