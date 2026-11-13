from datetime import datetime
from pathlib import Path
from threading import Lock

#Registra las acciones importantes realizadas en el sistema
class Auditoria:
    #Inicializa la ubicación del archivo de auditoría
    def __init__(self, ruta):
        self.ruta = Path(ruta)
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.cerrojo = Lock()

    #Agrega un nuevo registro al archivo de auditoría
    def registrar(self, accion, detalle):
        detalle = str(detalle).replace("\n", " ").replace("\r", " ")

    #Se utiliza append para conservar los registros anteriores.
        with self.cerrojo, self.ruta.open("a", encoding="utf-8") as archivo:
            archivo.write(
                f"[{datetime.now():%Y-%m-%d %H:%M:%S}] "
                f"{accion} | {detalle}\n"
            )