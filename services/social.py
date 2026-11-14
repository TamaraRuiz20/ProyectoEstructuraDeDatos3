import hashlib
import hmac
import secrets
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from models.usuario import Usuario
from models.publicacion import Publicacion
from structures.grafo_amistades import GrafoAmistades
from persistence.archivos import Archivos
from logs.auditoria import Auditoria

def hash_clave(clave, sal):
    return hashlib.pbkdf2_hmac("sha256", clave.encode(), bytes.fromhex(sal), 120000).hex()

class Social:
    """Servicio único y sencillo: usuarios, lista de publicaciones y grafo en memoria."""
    def __init__(self, carpeta):
        self.archivos = Archivos(Path(carpeta) / "data")
        self.log = Auditoria(Path(carpeta) / "logs" / "social_una.log")
        self.usuarios = {u["id"]: Usuario(**u) for u in self.archivos.leer("usuarios.json", [])}
        self.publicaciones = [Publicacion(**p) for p in self.archivos.leer("publicaciones.json", [])]
        self.grafo = GrafoAmistades(self.archivos.leer("amistades.json", {}))
        for uid in self.usuarios:
            self.grafo.agregar_usuario(uid)
        self.sesion = None

    def registrar(self, nombre, usuario, clave):
        nombre, usuario = nombre.strip(), usuario.strip().lower()
        if not 2 <= len(nombre) <= 80:
            raise ValueError("El nombre debe tener entre 2 y 80 caracteres.")
        if not re.fullmatch(r"[a-z0-9_]{3,24}", usuario):
            raise ValueError("Usuario: 3–24 letras sin tildes, números o guion bajo.")
        if any(u.usuario == usuario for u in self.usuarios.values()):
            raise ValueError("Ese usuario ya existe.")
        if not 6 <= len(clave) <= 128:
            raise ValueError("La contraseña debe tener entre 6 y 128 caracteres.")
        uid = max(self.usuarios, default=0) + 1
        sal = secrets.token_hex(16)
        nuevo = Usuario(uid, nombre, usuario, hash_clave(clave, sal), sal)
        self.usuarios[uid] = nuevo
        try:
            self.archivos.guardar("usuarios.json", [asdict(u) for u in self.usuarios.values()])
        except OSError:
            del self.usuarios[uid]
            raise
        self.grafo.agregar_usuario(uid)
        self.log.registrar("REGISTRO", f"Usuario: {usuario}")
        return nuevo

    def login(self, usuario, clave):
        usuario = usuario.strip().lower()
        encontrado = next((u for u in self.usuarios.values() if u.usuario == usuario), None)
        if encontrado and hmac.compare_digest(encontrado.clave_hash, hash_clave(clave, encontrado.sal)):
            self.sesion = encontrado
            self.log.registrar("LOGIN", f"Usuario: {usuario}")
            return encontrado
        self.log.registrar("LOGIN_FALLIDO", f"Usuario: {usuario}")
        raise ValueError("Usuario o contraseña incorrectos.")

    def cerrar_sesion(self):
        if self.sesion:
            self.log.registrar("LOGOUT", f"Usuario: {self.sesion.usuario}")
        self.sesion = None

    def exigir_sesion(self):
        if self.sesion is None:
            raise ValueError("Debes iniciar sesión.")
        return self.sesion.id

    def buscar(self, texto):
        texto = texto.strip().casefold()
        return [u for u in self.usuarios.values() if texto in u.nombre.casefold() or texto in u.usuario.casefold()]

    def agregar_amigo(self, destino):
        origen = self.exigir_sesion()
        if destino not in self.usuarios:
            raise ValueError("El usuario no existe.")
        self.grafo.agregar(origen, destino)
        try:
            self.archivos.guardar("amistades.json", self.grafo.a_dict())
        except OSError:
            self.grafo.adyacencia[origen].remove(destino)
            self.grafo.adyacencia[destino].remove(origen)
            raise
        self.log.registrar("AMISTAD", f"{self.sesion.usuario} -> {self.usuarios[destino].usuario}")

    def amigos(self):
        return [self.usuarios[i] for i in sorted(self.grafo.amigos(self.exigir_sesion()))]

    def publicar(self, contenido):
        uid = self.exigir_sesion()
        contenido = contenido.strip()
        if not 1 <= len(contenido) <= 2000:
            raise ValueError("La publicación debe tener entre 1 y 2000 caracteres.")
        p = Publicacion(max((p.id for p in self.publicaciones), default=0)+1, uid, contenido, datetime.now().astimezone().isoformat(timespec="microseconds"))
        self.publicaciones.append(p)
        try:
            self.archivos.guardar("publicaciones.json", [asdict(p) for p in self.publicaciones])
        except OSError:
            self.publicaciones.pop()
            raise
        self.log.registrar("PUBLICACION", f"Usuario: {self.sesion.usuario} | ID: {p.id}")
        return p

    def feed(self, solo_propias=False):
        uid = self.exigir_sesion()
        visibles = {uid} if solo_propias else self.grafo.amigos(uid) | {uid}
        return sorted((p for p in self.publicaciones if p.usuario_id in visibles), key=lambda p: (datetime.fromisoformat(p.fecha), p.id), reverse=True)
