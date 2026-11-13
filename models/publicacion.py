from dataclasses import dataclass

#Representa una publicación realizada por algun usuario
@dataclass
class Publicacion:
    id: int
    usuario_id: int
    contenido: str
    fecha: str
