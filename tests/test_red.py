import socket
import tempfile
import time
import unittest
from pathlib import Path
from logs.auditoria import Auditoria
from network.connection import Conexion

class PruebasRed(unittest.TestCase):
    def esperar(self, condicion):
        limite = time.monotonic() + 5
        while time.monotonic() < limite:
            if condicion(): return
            time.sleep(0.02)
        self.fail('Tiempo de espera agotado')

    def test_tcp_bidireccional_unicode_desconexion(self):
        with self.subTest():
            temporal = tempfile.TemporaryDirectory()
            self.addCleanup(temporal.cleanup)
            carpeta = temporal.name
            log = Auditoria(Path(carpeta)/'red.log')
            a, b = Conexion(log), Conexion(log)
            self.addCleanup(a.cerrar)
            self.addCleanup(b.cerrar)
            a.iniciar_servidor(0)
            puerto = a.servidor.getsockname()[1]
            b.conectar('127.0.0.1', puerto)
            self.esperar(lambda: a.socket is not None and b.socket is not None)
            a.enviar('tamara', '¡Hola! 🌻\nSegunda línea')
            b.enviar('amanda', 'Respuesta desde B')
            recibidos_a, recibidos_b = [], []
            def recibidos():
                for red, lista in [(a, recibidos_a), (b, recibidos_b)]:
                    while not red.eventos.empty(): lista.append(red.eventos.get_nowait())
                return ('mensaje', 'amanda: Respuesta desde B') in recibidos_a and ('mensaje', 'tamara: ¡Hola! 🌻\nSegunda línea') in recibidos_b
            self.esperar(recibidos)
            b.cerrar()
            self.esperar(lambda: a.socket is None)
            self.assertIn('ENVIO', (Path(carpeta)/'red.log').read_text())
            self.assertIn('RECEPCION', (Path(carpeta)/'red.log').read_text())

    def test_tramas_fragmentadas_y_concatenadas(self):
        with self.subTest():
            temporal = tempfile.TemporaryDirectory()
            self.addCleanup(temporal.cleanup)
            carpeta = temporal.name
            a = Conexion(Auditoria(Path(carpeta)/'red.log'))
            self.addCleanup(a.cerrar)
            a.iniciar_servidor(0)
            cliente = socket.create_connection(('127.0.0.1', a.servidor.getsockname()[1]))
            self.addCleanup(cliente.close)
            cliente.sendall(b'{"autor":"jeff",')
            cliente.sendall(b'"texto":"uno"}\n{"autor":"jeff","texto":"dos"}\n')
            eventos = []
            def recibido():
                while not a.eventos.empty(): eventos.append(a.eventos.get_nowait())
                return len([e for e in eventos if e[0]=='mensaje']) == 2
            self.esperar(recibido)
            self.assertIn(('mensaje', 'jeff: uno'), eventos)
            self.assertIn(('mensaje', 'jeff: dos'), eventos)

if __name__ == '__main__': unittest.main()
