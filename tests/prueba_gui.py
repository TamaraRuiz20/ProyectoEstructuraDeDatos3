"""Prueba de integración gráfica. Ejecutar: python -m tests.prueba_gui"""
import tempfile
import time
from pathlib import Path
from unittest.mock import patch
import customtkinter as ctk
from gui.app import Aplicacion
from services.social import Social


def botones(widget):
    resultado = []
    for hijo in widget.winfo_children():
        if isinstance(hijo, ctk.CTkButton): resultado.append(hijo)
        resultado.extend(botones(hijo))
    return resultado


def pulsar(app, texto):
    encontrados = [b for b in botones(app) if b.cget('text') == texto]
    assert encontrados, f'No se encontró el botón {texto}'
    encontrados[0].invoke()
    app.update()


def main():
    ctk.set_appearance_mode('light')
    errores = []
    with tempfile.TemporaryDirectory() as carpeta, patch('gui.app.messagebox.showinfo'), patch('gui.app.messagebox.showerror') as alertas:
        s = Social(carpeta)
        s.registrar('Amanda', 'amanda', 'una123')
        s.login('amanda', 'una123')
        s.publicar('Publicación de Amanda')
        s.cerrar_sesion()
        app = Aplicacion(s)
        app.report_callback_exception = lambda *error: errores.append(error)
        try:
            app.update()
            pulsar(app, 'Crear una cuenta')
            app.nombre.insert(0, 'Tamara')
            app.usuario.insert(0, 'tamara')
            app.clave.insert(0, 'una123')
            pulsar(app, 'Registrarme')
            app.usuario.insert(0, 'tamara')
            app.clave.insert(0, 'una123')
            pulsar(app, 'Iniciar sesión  →')
            assert s.sesion.usuario == 'tamara'
            pulsar(app, 'Buscar')
            app.busqueda.insert(0, 'amanda')
            pulsar(app, 'Buscar estudiantes')
            pulsar(app, 'Agregar')
            assert len(s.amigos()) == 1
            pulsar(app, 'Amigos')
            pulsar(app, 'Publicar')
            app.texto_publicacion.insert('1.0', 'Publicación creada desde la interfaz')
            [b for b in botones(app.contenido) if b.cget('text') == 'Publicar'][0].invoke()
            app.update()
            assert len(s.feed()) == 2
            pulsar(app, 'Perfil')
            pulsar(app, 'Red local')
            app.update()
            pulsar(app, 'Cerrar sesión')
            assert s.sesion is None
            assert not errores, errores
            assert not alertas.called, alertas.call_args_list
        finally:
            app.cerrar()
        # Cerrar y reconstruir tanto el servicio como la ventana.
        recargado = Social(carpeta)
        segunda = Aplicacion(recargado)
        try:
            segunda.update()
            segunda.usuario.insert(0, 'tamara')
            segunda.clave.insert(0, 'una123')
            pulsar(segunda, 'Iniciar sesión  →')
            assert len(recargado.feed()) == 2
            assert len(recargado.amigos()) == 1
            assert len(recargado.publicaciones) == 2
            assert 'PUBLICACION' in (Path(carpeta)/'logs/social_una.log').read_text()
        finally:
            segunda.cerrar()
    print('GUI OK: registro, login, búsqueda, amistad, publicación, feed, perfil, red local, logout y reapertura.')

if __name__ == '__main__': main()
