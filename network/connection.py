import json
import socket
import threading
from queue import Queue
from network.server import abrir_servidor
from network.client import conectar

class Conexion:
    """Una conversación TCP. Los hilos dejan eventos; solo la GUI toca widgets."""
    def __init__(self, log):
        self.log = log
        self.eventos = Queue()
        self.servidor = None
        self.socket = None
        self.cerrojo = threading.Lock()
        self.cerrojo_envio = threading.Lock()
        self.generacion = 0
        self.ocupado = False

    def estado(self, texto):
        self.eventos.put(("estado", texto))

    def iniciar_servidor(self, puerto):
        if self.servidor or self.socket or self.ocupado:
            raise ValueError("Desconecta la sesión de red antes de iniciar otra.")
        servidor = abrir_servidor(puerto)
        self.servidor = servidor
        generacion = self.generacion
        self.estado(f"Esperando conexión en puerto {servidor.getsockname()[1]}")
        self.log.registrar("SERVIDOR", f"Puerto: {servidor.getsockname()[1]}")
        def aceptar():
            while generacion == self.generacion:
                try:
                    cliente, direccion = servidor.accept()
                    self._activar(cliente, direccion[0], generacion)
                    break
                except socket.timeout:
                    continue
                except OSError:
                    break
            servidor.close()
            if self.servidor is servidor:
                self.servidor = None
        threading.Thread(target=aceptar, daemon=True).start()

    def conectar(self, ip, puerto):
        if self.servidor or self.socket or self.ocupado:
            raise ValueError("Desconecta la sesión de red antes de iniciar otra.")
        self.ocupado = True
        generacion = self.generacion
        self.estado("Conectando…")
        def trabajo():
            try:
                cliente = conectar(ip, puerto)
                self._activar(cliente, ip, generacion)
            except (OSError, ValueError) as error:
                if generacion == self.generacion:
                    self.estado("Desconectado")
                    self.eventos.put(("error", f"No se pudo conectar: {error}"))
                    self.log.registrar("RED_ERROR", str(error))
            finally:
                if generacion == self.generacion:
                    self.ocupado = False
        threading.Thread(target=trabajo, daemon=True).start()

    def _activar(self, cliente, ip, generacion):
        with self.cerrojo:
            if generacion != self.generacion:
                cliente.close()
                return
            self.socket = cliente
        cliente.settimeout(0.5)
        self.estado(f"Conectado con {ip}")
        self.log.registrar("CONEXION", f"IP: {ip}")
        threading.Thread(target=self._recibir, args=(cliente, generacion), daemon=True).start()

    def _recibir(self, cliente, generacion):
        pendiente = b""
        try:
            while generacion == self.generacion:
                try:
                    parte = cliente.recv(4096)
                except socket.timeout:
                    continue
                if not parte:
                    break
                pendiente += parte
                # Límite por trama para que una conexión no acumule memoria sin fin.
                while b"\n" in pendiente:
                    linea, pendiente = pendiente.split(b"\n", 1)
                    if len(linea) > 20000:
                        raise ValueError("Mensaje demasiado grande.")
                    dato = json.loads(linea.decode("utf-8"))
                    if not isinstance(dato, dict):
                        raise ValueError("Formato de mensaje inválido.")
                    autor, texto = dato.get("autor"), dato.get("texto")
                    if not isinstance(autor, str) or not isinstance(texto, str) or not 1 <= len(texto.strip()) <= 2000 or len(autor) > 80:
                        raise ValueError("Mensaje inválido.")
                    if generacion == self.generacion:
                        self.eventos.put(("mensaje", f"{autor}: {texto}"))
                        self.log.registrar("RECEPCION", f"Autor remoto: {autor}")
                if len(pendiente) > 20000:
                    raise ValueError("Mensaje demasiado grande.")
        except (OSError, ValueError, UnicodeError) as error:
            if generacion == self.generacion:
                self.eventos.put(("error", f"Conexión interrumpida: {error}"))
        finally:
            cliente.close()
            with self.cerrojo:
                if self.socket is cliente:
                    self.socket = None
                    self.estado("Desconectado")
                    self.log.registrar("DESCONEXION", "Conexión finalizada")

    def enviar(self, autor, texto):
        texto = texto.strip()
        if not 1 <= len(texto) <= 2000:
            raise ValueError("Escribe un mensaje de 1 a 2000 caracteres.")
        cliente = self.socket
        if cliente is None:
            raise ValueError("Primero establece una conexión.")
        # El envío también ocurre fuera del hilo de la interfaz.
        generacion = self.generacion
        def trabajo():
            try:
                paquete = json.dumps({"autor": autor, "texto": texto}, ensure_ascii=False).encode("utf-8") + b"\n"
                with self.cerrojo_envio:
                    cliente.sendall(paquete)
                if generacion == self.generacion:
                    self.eventos.put(("mensaje", f"Tú: {texto}"))
                    self.log.registrar("ENVIO", f"Usuario: {autor}")
            except OSError as error:
                if generacion == self.generacion:
                    self.eventos.put(("error", f"No se pudo enviar: {error}"))
                    try:
                        cliente.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    cliente.close()
        threading.Thread(target=trabajo, daemon=True).start()

    def cerrar(self):
        with self.cerrojo:
            self.generacion += 1
            self.ocupado = False
            for conexion in (self.socket, self.servidor):
                if conexion:
                    try:
                        conexion.shutdown(socket.SHUT_RDWR)
                    except OSError:
                        pass
                    conexion.close()
            self.socket = self.servidor = None
        self.estado("Desconectado")
        self.log.registrar("DESCONEXION", "Cierre local")
