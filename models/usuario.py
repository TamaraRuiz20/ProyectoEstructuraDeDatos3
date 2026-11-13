from dataclasses import dataclass

#Representa un usuario registrado en Social UNA
@dataclass
class Usuario:
    id: int
    nombre: str
    usuario: str
    clave_hash: str
    sal: str