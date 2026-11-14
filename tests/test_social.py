import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from services.social import Social

class PruebasSocial(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.ruta = Path(self.temporal.name)
        self.s = Social(self.ruta)
        self.a = self.s.registrar('Tamara', 'tamara', 'una123')
        self.b = self.s.registrar('Amanda', 'amanda', 'una123')
        self.c = self.s.registrar('Jeff', 'jeff', 'una123')

    def test_registro_validaciones_y_login(self):
        for args in [('Otro', 'TAMARA', 'una123'), ('A', 'otro', 'una123'), ('Otro', 'otro', '1')]:
            with self.assertRaises(ValueError):
                self.s.registrar(*args)
        with self.assertRaises(ValueError):
            self.s.login('tamara', 'incorrecta')
        self.assertEqual(self.s.login(' TAMARA ', 'una123').id, self.a.id)
        datos = (self.ruta/'data/usuarios.json').read_text()
        self.assertNotIn('una123', datos)
        self.assertNotEqual(self.a.sal, self.b.sal)

    def test_grafo_feed_persistencia_logs(self):
        self.s.login('amanda', 'una123')
        p1 = self.s.publicar('Hola de Amanda')
        self.s.login('jeff', 'una123')
        self.s.publicar('Esta no debe aparecer')
        self.s.login('tamara', 'una123')
        p2 = self.s.publicar('Hola de Tamara')
        self.assertEqual([p.id for p in self.s.feed()], [p2.id])
        self.s.agregar_amigo(self.b.id)
        for destino in [self.a.id, self.b.id, 999]:
            with self.assertRaises(ValueError):
                self.s.agregar_amigo(destino)
        self.assertEqual(self.s.grafo.amigos(self.b.id), {self.a.id})
        self.assertEqual([p.id for p in self.s.feed()], [p2.id, p1.id])
        self.assertEqual([u.usuario for u in self.s.buscar('AMAN')], ['amanda'])
        self.s.cerrar_sesion()
        reabierto = Social(self.ruta)
        reabierto.login('tamara', 'una123')
        self.assertEqual([p.id for p in reabierto.feed()], [p2.id, p1.id])
        self.assertEqual([u.id for u in reabierto.amigos()], [self.b.id])
        self.assertEqual(len(reabierto.feed(True)), 1)
        log = (self.ruta/'logs/social_una.log').read_text()
        for accion in ['REGISTRO', 'LOGIN', 'AMISTAD', 'PUBLICACION', 'LOGOUT']:
            self.assertIn(accion, log)

    def test_error_escritura_revierte_memoria(self):
        self.s.login('tamara', 'una123')
        with patch.object(self.s.archivos, 'guardar', side_effect=OSError('Disco no disponible')):
            with self.assertRaises(OSError): self.s.agregar_amigo(self.b.id)
            with self.assertRaises(OSError): self.s.publicar('No persistida')
            with self.assertRaises(OSError): self.s.registrar('Allison', 'allison', 'una123')
        self.assertEqual(len(self.s.usuarios), 3)
        self.assertFalse(self.s.publicaciones)
        self.assertFalse(self.s.grafo.amigos(self.a.id))

    def test_archivo_danado_no_se_sobrescribe(self):
        ruta = self.ruta/'data/usuarios.json'
        ruta.write_text('{invalido', encoding='utf-8')
        with self.assertRaises(ValueError): Social(self.ruta)
        self.assertEqual(ruta.read_text(), '{invalido')

if __name__ == '__main__': unittest.main()
