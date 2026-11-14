from datetime import datetime
from queue import Empty
from tkinter import messagebox
import customtkinter as ctk
from network.connection import Conexion
from network.client import ip_local

# ---- Paleta roja y blanca (cambiar aquí cambia toda la interfaz) ----
ROJO = "#A31E32"        # color principal (rojo institucional UNA)
ROJO_OSC = "#7F1727"    # hover / tonos oscuros
ROJO_CLARO = "#F8E9EC"  # fondos suaves y hover de botones planos
FONDO = "#F7F2F3"       # fondo general (blanco cálido)
BORDE = "#EAD7DB"       # bordes finos de tarjetas y campos
TEXTO = "#1E1417"
GRIS = "#7B6A6E"
CAMPO = "#FBF6F7"       # fondo de cuadros de texto
PALETA_AVATAR = ["#A31E32", "#7F1727", "#B23A48", "#8C2F39", "#C0475A", "#6D1A2B"]
ICONOS = {"Inicio": "🏠", "Amigos": "👥", "Buscar": "🔍", "Publicar": "📝", "Red local": "💬", "Perfil": "👤"}


def iniciales(nombre):
    """'Tamara Pérez' -> 'TP'. Se usa como foto de perfil."""
    return "".join(p[0] for p in nombre.split()[:2]).upper() or "?"


def tiempo_relativo(fecha_iso):
    """Convierte la fecha guardada en un texto tipo 'hace 5 min'."""
    fecha = datetime.fromisoformat(fecha_iso)
    if fecha.tzinfo is None:
        fecha = fecha.astimezone()
    segundos = (datetime.now().astimezone() - fecha).total_seconds()
    if segundos < 60:
        return "ahora"
    if segundos < 3600:
        return f"hace {int(segundos // 60)} min"
    if segundos < 86400:
        return f"hace {int(segundos // 3600)} h"
    if segundos < 7 * 86400:
        return f"hace {int(segundos // 86400)} d"
    return fecha.strftime("%d/%m/%Y")


class Aplicacion(ctk.CTk):
    def __init__(self, social):
        super().__init__()
        self.social = social
        self.red = Conexion(social.log)
        self.historial = []
        self.estado_red = "Desconectado"
        self.title("Social UNA · Red estudiantil")
        self.geometry("1120x760")
        self.minsize(920, 660)
        self.configure(fg_color=FONDO)
        self.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.mostrar_login()
        self.after(100, self.procesar_red)

    def limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()

    def etiqueta(self, padre, texto, tam=14, color=TEXTO, bold=False, **opciones):
        return ctk.CTkLabel(padre, text=texto, text_color=color,
                            font=("Segoe UI", tam, "bold" if bold else "normal"), **opciones)

    def boton(self, padre, texto, funcion, **opciones):
        return ctk.CTkButton(padre, text=texto, command=funcion, height=40,
                            corner_radius=20, fg_color=ROJO, hover_color=ROJO_OSC,
                            text_color="white", font=("Segoe UI", 14, "bold"), **opciones)

    def campo(self, padre, texto, secreto=False):
        campo = ctk.CTkEntry(padre, placeholder_text=texto, height=44, corner_radius=12,
                             show="•" if secreto else "", fg_color=CAMPO,
                             border_color=BORDE, text_color=TEXTO)
        campo.pack(fill="x", pady=7)
        return campo

    def avatar(self, padre, usuario, tam=44):
        """Círculo de color con las iniciales, como foto de perfil."""
        return ctk.CTkLabel(padre, text=iniciales(usuario.nombre), width=tam, height=tam,
                            corner_radius=tam // 2,
                            fg_color=PALETA_AVATAR[usuario.id % len(PALETA_AVATAR)],
                            text_color="white", font=("Segoe UI", int(tam * 0.38), "bold"))

    def ejecutar(self, accion):
        try:
            return accion()
        except (ValueError, OSError) as error:
            messagebox.showerror("Social UNA", str(error), parent=self)

    def mostrar_login(self, registro=False):
        self.limpiar()
        marco = ctk.CTkFrame(self, fg_color="white", corner_radius=22)
        marco.pack(fill="both", expand=True, padx=45, pady=45)
        marca = ctk.CTkFrame(marco, fg_color=ROJO, corner_radius=20, width=370)
        marca.pack(side="left", fill="both", padx=14, pady=14)
        marca.pack_propagate(False)
        self.etiqueta(marca, "UNA / COMUNIDAD", 14, "#FFD3D8", True).pack(anchor="w", padx=32, pady=(45, 45))
        self.etiqueta(marca, "Social\nUNA", 54, "white", True, justify="left").pack(anchor="w", padx=32)
        self.etiqueta(marca, "Tu campus.\nTus amigos.\nTus ideas.", 23, "#FFE9EB", justify="left").pack(anchor="w", padx=32, pady=30)
        self.etiqueta(marca, "RED SOCIAL ESTUDIANTIL", 12, "#FFD3D8").pack(side="bottom", pady=32)
        form = ctk.CTkFrame(marco, fg_color="transparent")
        form.pack(side="left", fill="both", expand=True, padx=45, pady=65)
        self.etiqueta(form, "Crea tu cuenta" if registro else "Qué bueno verte", 30, bold=True).pack(anchor="w")
        self.etiqueta(form, "Conecta con tu comunidad universitaria.", 14, GRIS).pack(anchor="w", pady=(8, 25))
        if registro:
            self.nombre = self.campo(form, "Nombre completo")
        self.usuario = self.campo(form, "Usuario")
        self.clave = self.campo(form, "Contraseña", True)
        def ingresar():
            self.social.login(self.usuario.get(), self.clave.get())
            self.principal()
        def registrar():
            self.social.registrar(self.nombre.get(), self.usuario.get(), self.clave.get())
            messagebox.showinfo("Cuenta creada", "Ya puedes iniciar sesión.", parent=self)
            self.mostrar_login()
        accion = registrar if registro else ingresar
        self.boton(form, "Registrarme" if registro else "Iniciar sesión  →", lambda: self.ejecutar(accion)).pack(fill="x", pady=(20, 12))
        ctk.CTkButton(form, text="Ya tengo cuenta" if registro else "Crear una cuenta", command=lambda: self.mostrar_login(not registro), fg_color="transparent", text_color=ROJO, hover_color=ROJO_CLARO, height=38, corner_radius=20).pack(fill="x")
        self.clave.bind("<Return>", lambda e: self.ejecutar(accion))

    def principal(self):
        self.limpiar()
        lateral = ctk.CTkFrame(self, fg_color="white", width=225, corner_radius=0)
        lateral.pack(side="left", fill="y")
        lateral.pack_propagate(False)
        ctk.CTkFrame(self, fg_color=BORDE, width=1, corner_radius=0).pack(side="left", fill="y")
        self.lateral = lateral
        self.menu_abierto = True
        self.destino_menu = 225
        ctk.CTkButton(lateral, text="☰", width=44, height=36, corner_radius=10, fg_color="transparent", text_color=ROJO, hover_color=ROJO_CLARO, font=("Segoe UI", 20, "bold"), command=self.alternar_menu).pack(anchor="w", padx=15, pady=(18, 0))
        self.titulo_menu = self.etiqueta(lateral, "Social UNA", 28, ROJO, True)
        self.titulo_menu.pack(pady=(10, 0))
        self.sub_menu = self.etiqueta(lateral, "TU COMUNIDAD", 11, GRIS)
        self.sub_menu.pack(pady=(0, 30))
        self.botones = {}
        for nombre in ["Inicio", "Amigos", "Buscar", "Publicar", "Red local", "Perfil"]:
            b = ctk.CTkButton(lateral, text=nombre, anchor="w", height=44, corner_radius=12, fg_color="transparent", text_color=TEXTO, hover_color=ROJO_CLARO, font=("Segoe UI", 15, "bold"), command=lambda n=nombre: self.pagina(n))
            b.pack(fill="x", padx=18, pady=4)
            self.botones[nombre] = b
        self.btn_cerrar = ctk.CTkButton(lateral, text="Cerrar sesión", command=self.salir_sesion, fg_color="transparent", border_width=2, border_color=ROJO, text_color=ROJO, hover_color=ROJO_CLARO, height=40, corner_radius=20)
        self.btn_cerrar.pack(side="bottom", fill="x", padx=18, pady=(8, 25))
        self.chip = ctk.CTkFrame(lateral, fg_color=ROJO_CLARO, corner_radius=14)
        self.chip.pack(side="bottom", fill="x", padx=18, pady=5)
        self.avatar(self.chip, self.social.sesion, 38).pack(side="left", padx=(10, 8), pady=10)
        datos = ctk.CTkFrame(self.chip, fg_color="transparent")
        datos.pack(side="left", fill="x", expand=True)
        self.etiqueta(datos, self.social.sesion.nombre.split()[0], 14, bold=True, anchor="w").pack(fill="x")
        self.etiqueta(datos, "@" + self.social.sesion.usuario, 12, GRIS, anchor="w").pack(fill="x")
        self.contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.contenido.pack(side="left", fill="both", expand=True, padx=32, pady=28)
        self.pagina("Inicio")

    def alternar_menu(self):
        """Pliega el menú lateral a solo iconos, o lo vuelve a desplegar."""
        self.menu_abierto = not self.menu_abierto
        abierto = self.menu_abierto
        self.titulo_menu.configure(text="Social UNA" if abierto else "UNA",
                                   font=("Segoe UI", 28 if abierto else 20, "bold"))
        self.sub_menu.configure(text="TU COMUNIDAD" if abierto else "")
        for nombre, b in self.botones.items():
            b.configure(text=nombre if abierto else ICONOS[nombre],
                        anchor="w" if abierto else "center")
        self.btn_cerrar.configure(text="Cerrar sesión" if abierto else "✕")
        if abierto:
            self.chip.pack(side="bottom", fill="x", padx=18, pady=5)
        else:
            self.chip.pack_forget()
        self.destino_menu = 225 if abierto else 76
        self.animar_menu(self.destino_menu)

    def animar_menu(self, destino):
        """Cambia el ancho del menú poco a poco para que se vea animado."""
        if destino != self.destino_menu or not self.lateral.winfo_exists():
            return
        actual = self.lateral.cget("width")
        if actual == destino:
            return
        paso = 38 if destino > actual else -38
        nuevo = actual + paso
        if (paso > 0 and nuevo >= destino) or (paso < 0 and nuevo <= destino):
            nuevo = destino
        self.lateral.configure(width=nuevo)
        if nuevo != destino:
            self.after(12, lambda: self.animar_menu(destino))

    def pagina(self, nombre):
        self.pagina_actual = nombre
        for n, b in self.botones.items():
            activo = n == nombre
            b.configure(fg_color=ROJO if activo else "transparent",
                        text_color="white" if activo else TEXTO,
                        hover_color=ROJO_OSC if activo else ROJO_CLARO)
        for w in self.contenido.winfo_children():
            w.destroy()
        subtitulos = {"Inicio": "Las novedades de tu círculo universitario.", "Amigos": "Las personas con quienes conectas.", "Buscar": "Encuentra estudiantes y amplía tu círculo.", "Publicar": "Comparte una idea con tus amigos.", "Red local": "Mensajes de texto entre dos computadoras.", "Perfil": "Tu espacio en Social UNA."}
        self.etiqueta(self.contenido, nombre, 30, bold=True).pack(anchor="w")
        self.etiqueta(self.contenido, subtitulos[nombre], 14, GRIS).pack(anchor="w", pady=(3, 20))
        self.cuerpo = ctk.CTkScrollableFrame(self.contenido, fg_color="transparent", scrollbar_button_color="#E3C9CF", scrollbar_button_hover_color=ROJO)
        self.cuerpo.pack(fill="both", expand=True)
        {"Inicio": self.muro, "Amigos": self.ver_amigos, "Buscar": self.buscar, "Publicar": self.editor, "Red local": self.red_local, "Perfil": self.perfil}[nombre]()

    def tarjeta(self, padre=None):
        tarjeta = ctk.CTkFrame(padre or self.cuerpo, fg_color="white", corner_radius=16, border_width=1, border_color=BORDE)
        tarjeta.pack(fill="x", pady=(0, 14))
        return tarjeta

    def compositor(self):
        """Cuadro rápido '¿Qué estás pensando?' arriba del muro."""
        card = self.tarjeta()
        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=20, pady=(16, 8))
        self.avatar(fila, self.social.sesion, 40).pack(side="left")
        self.etiqueta(fila, "¿Qué estás pensando, " + self.social.sesion.nombre.split()[0] + "?", 16, bold=True).pack(side="left", padx=12)
        self.texto_rapido = ctk.CTkTextbox(card, height=80, fg_color=CAMPO, text_color=TEXTO, border_width=1, border_color=BORDE, corner_radius=12, font=("Segoe UI", 14))
        self.texto_rapido.pack(fill="x", padx=20)
        def enviar():
            self.social.publicar(self.texto_rapido.get("1.0", "end-1c"))
            self.pagina("Inicio")
        self.boton(card, "Publicar", lambda: self.ejecutar(enviar), width=130).pack(anchor="e", padx=20, pady=(10, 16))

    def ajustar_texto(self, tarjeta, etiqueta, margen=60):
        """Hace que el texto use todo el ancho de la tarjeta al cambiar el tamaño de la ventana."""
        def ajustar(evento):
            nuevo = max(200, evento.width - margen)
            if etiqueta.cget("wraplength") != nuevo:
                etiqueta.configure(wraplength=nuevo)
        tarjeta.bind("<Configure>", ajustar)

    def banner(self):
        """Tarjeta roja de bienvenida arriba del muro."""
        yo = self.social.sesion
        n = len(self.social.amigos())
        if n == 0:
            frase = "Aún no tienes amigos. ¡Agrega a alguien para llenar tu muro!"
        else:
            frase = f"Tienes {n} {'amigo' if n == 1 else 'amigos'}. Mira qué hay de nuevo en tu círculo."
        card = ctk.CTkFrame(self.cuerpo, fg_color=ROJO, corner_radius=18)
        card.pack(fill="x", pady=(0, 14))
        self.etiqueta(card, "Hola, " + yo.nombre.split()[0], 26, "white", True).pack(anchor="w", padx=24, pady=(20, 2))
        self.etiqueta(card, frase, 14, "#FFE9EB").pack(anchor="w", padx=24, pady=(0, 20))

    def sugerencias(self):
        """Fila de personas que el usuario todavía no tiene como amigos."""
        yo = self.social.sesion.id
        amigos = self.social.grafo.amigos(yo)
        candidatos = [u for u in self.social.usuarios.values() if u.id != yo and u.id not in amigos][:4]
        if not candidatos:
            return
        self.etiqueta(self.cuerpo, "Personas que quizá conozcas", 18, bold=True).pack(anchor="w", pady=(0, 8))
        fila = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        fila.pack(fill="x", pady=(0, 14))
        for u in candidatos:
            mini = ctk.CTkFrame(fila, fg_color="white", corner_radius=16, border_width=1, border_color=BORDE)
            mini.pack(side="left", padx=(0, 10))
            self.avatar(mini, u, 52).pack(padx=22, pady=(14, 6))
            self.etiqueta(mini, u.nombre.split()[0], 14, bold=True).pack()
            self.etiqueta(mini, "@" + u.usuario, 11, GRIS).pack()
            def agregar(uid=u.id):
                self.social.agregar_amigo(uid)
                self.pagina("Inicio")
            self.boton(mini, "Agregar", lambda a=agregar: self.ejecutar(a), width=100).pack(padx=14, pady=(8, 14))

    def muro(self, propias=False):
        if not propias:
            self.banner()
            self.compositor()
            self.sugerencias()
            self.etiqueta(self.cuerpo, "Publicaciones recientes", 18, bold=True).pack(anchor="w", pady=(6, 10))
        publicaciones = self.social.feed(propias)
        if not publicaciones:
            self.etiqueta(self.cuerpo, "Aún no hay publicaciones. Comparte la primera.", color=GRIS).pack(pady=30)
        yo = self.social.sesion.id
        for p in publicaciones:
            u = self.social.usuarios[p.usuario_id]
            card = self.tarjeta()
            cabecera = ctk.CTkFrame(card, fg_color="transparent")
            cabecera.pack(fill="x", padx=20, pady=(16, 0))
            self.avatar(cabecera, u, 44).pack(side="left")
            datos = ctk.CTkFrame(cabecera, fg_color="transparent")
            datos.pack(side="left", padx=12)
            self.etiqueta(datos, u.nombre, 16, bold=True, anchor="w").pack(fill="x")
            self.etiqueta(datos, "@" + u.usuario + "  ·  " + tiempo_relativo(p.fecha), 12, GRIS, anchor="w").pack(fill="x")
            if p.usuario_id == yo and not propias:
                self.etiqueta(cabecera, " Tú ", 12, ROJO, True, fg_color=ROJO_CLARO, corner_radius=8).pack(side="right")
            texto = self.etiqueta(card, p.contenido, 15, justify="left", anchor="w", wraplength=520)
            texto.pack(fill="x", padx=20, pady=(12, 20))
            self.ajustar_texto(card, texto)

    def fila_usuario(self, u, agregar=False):
        card = self.tarjeta()
        self.avatar(card, u, 46).pack(side="left", padx=(18, 12), pady=14)
        datos = ctk.CTkFrame(card, fg_color="transparent")
        datos.pack(side="left")
        self.etiqueta(datos, u.nombre, 15, bold=True, anchor="w").pack(fill="x")
        self.etiqueta(datos, "@" + u.usuario, 12, GRIS, anchor="w").pack(fill="x")
        if agregar:
            amigo = u.id in self.social.grafo.amigos(self.social.sesion.id)
            propio = u.id == self.social.sesion.id
            def accion():
                self.social.agregar_amigo(u.id)
                self.resultados_busqueda()
                messagebox.showinfo("Amistad", "Amigo agregado correctamente.", parent=self)
            b = self.boton(card, "Tu cuenta" if propio else "Ya son amigos" if amigo else "Agregar", lambda: self.ejecutar(accion), width=125)
            b.pack(side="right", padx=18)
            if propio or amigo:
                b.configure(state="disabled")

    def ver_amigos(self):
        amigos = self.social.amigos()
        self.etiqueta(self.cuerpo, f"{len(amigos)} amigos", color=GRIS).pack(anchor="w", pady=(0, 12))
        for u in amigos:
            self.fila_usuario(u)
        if not amigos:
            self.etiqueta(self.cuerpo, "Busca estudiantes para agregar a tus primeros amigos.", color=GRIS).pack(pady=30)

    def buscar(self):
        self.busqueda = self.campo(self.cuerpo, "Busca por nombre o usuario")
        self.boton(self.cuerpo, "Buscar estudiantes", self.resultados_busqueda).pack(anchor="w", pady=(5, 15))
        self.busqueda.bind("<Return>", lambda e: self.resultados_busqueda())
        self.resultados = ctk.CTkFrame(self.cuerpo, fg_color="transparent")
        self.resultados.pack(fill="both", expand=True)
        self.resultados_busqueda()

    def resultados_busqueda(self):
        for w in self.resultados.winfo_children():
            w.destroy()
        usuarios = self.social.buscar(self.busqueda.get())
        self.etiqueta(self.resultados, f"{len(usuarios)} resultados", color=GRIS).pack(anchor="w", pady=10)
        # Reutilizamos la tarjeta habitual dentro del panel de resultados.
        anterior = self.cuerpo
        self.cuerpo = self.resultados
        for u in usuarios:
            self.fila_usuario(u, True)
        self.cuerpo = anterior

    def editor(self):
        card = self.tarjeta()
        self.etiqueta(card, "¿Qué quieres compartir, " + self.social.sesion.nombre + "?", 17, bold=True).pack(anchor="w", padx=20, pady=20)
        self.texto_publicacion = ctk.CTkTextbox(card, height=240, fg_color=CAMPO, text_color=TEXTO, border_width=1, border_color=BORDE, corner_radius=12, font=("Segoe UI", 15))
        self.texto_publicacion.pack(fill="x", padx=20)
        self.etiqueta(card, "Solo texto · Máximo 2000 caracteres", 12, GRIS).pack(anchor="w", padx=20, pady=10)
        def publicar():
            self.social.publicar(self.texto_publicacion.get("1.0", "end-1c"))
            self.pagina("Inicio")
            messagebox.showinfo("Publicado", "Tu publicación ya está en el muro.", parent=self)
        self.boton(card, "Publicar", lambda: self.ejecutar(publicar)).pack(anchor="e", padx=20, pady=20)

    def perfil(self):
        u = self.social.sesion
        card = self.tarjeta()
        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=24, pady=24)
        self.avatar(fila, u, 84).pack(side="left")
        datos = ctk.CTkFrame(fila, fg_color="transparent")
        datos.pack(side="left", padx=20)
        self.etiqueta(datos, u.nombre, 24, bold=True, anchor="w").pack(fill="x")
        self.etiqueta(datos, "@" + u.usuario, 14, GRIS, anchor="w").pack(fill="x", pady=(2, 8))
        self.etiqueta(datos, f"{len(self.social.amigos())} amigos  ·  {len(self.social.feed(True))} publicaciones  ·  ID de estudiante: {u.id}", 13, anchor="w").pack(fill="x")
        self.etiqueta(self.cuerpo, "Mis publicaciones", 20, bold=True).pack(anchor="w", pady=15)
        self.muro(True)

    def red_local(self):
        card = self.tarjeta()
        try:
            ip = ip_local()
        except OSError:
            ip = "Consulta ipconfig en Windows"
        self.etiqueta(card, "Tu IP local: " + ip, 16, bold=True).pack(anchor="w", padx=18, pady=(18, 5))
        self.estado_widget = self.etiqueta(card, self.estado_red, 14)
        self.estado_widget.pack(anchor="w", padx=18, pady=5)
        self.actualizar_estado()
        fila = ctk.CTkFrame(card, fg_color="transparent")
        fila.pack(fill="x", padx=18, pady=10)
        self.ip_destino = ctk.CTkEntry(fila, placeholder_text="IP de la otra computadora", height=40, corner_radius=12, fg_color=CAMPO, border_color=BORDE, text_color=TEXTO)
        self.ip_destino.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.puerto = ctk.CTkEntry(fila, width=90, height=40, corner_radius=12, fg_color=CAMPO, border_color=BORDE, text_color=TEXTO)
        self.puerto.insert(0, "5000")
        self.puerto.pack(side="left")
        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(fill="x", padx=18, pady=(0, 15))
        def puerto():
            try:
                valor = int(self.puerto.get())
            except ValueError:
                raise ValueError("El puerto debe ser un número de 1 a 65535.")
            if not 1 <= valor <= 65535:
                raise ValueError("El puerto debe estar entre 1 y 65535.")
            return valor
        self.boton(botones, "Iniciar servidor", lambda: self.ejecutar(lambda: self.red.iniciar_servidor(puerto())), width=145).pack(side="left", padx=(0, 8))
        self.boton(botones, "Conectar", lambda: self.ejecutar(lambda: self.red.conectar(self.ip_destino.get().strip(), puerto())), width=110).pack(side="left", padx=(0, 8))
        self.boton(botones, "Desconectar", self.red.cerrar, width=115).pack(side="left")
        self.etiqueta(self.cuerpo, "Una computadora inicia el servidor; la otra se conecta a su IP.", 12, GRIS).pack(anchor="w", pady=(0, 10))
        self.chat = ctk.CTkTextbox(self.cuerpo, height=210, fg_color="white", text_color=TEXTO, border_width=1, border_color=BORDE, corner_radius=12, font=("Segoe UI", 14))
        self.chat.pack(fill="x")
        self.dibujar_chat()
        self.mensaje = self.campo(self.cuerpo, "Escribe un mensaje…")
        def enviar():
            self.red.enviar(self.social.sesion.usuario, self.mensaje.get())
            self.mensaje.delete(0, "end")
        self.boton(self.cuerpo, "Enviar mensaje", lambda: self.ejecutar(enviar)).pack(anchor="e", pady=5)
        self.mensaje.bind("<Return>", lambda e: self.ejecutar(enviar))

    def actualizar_estado(self):
        if hasattr(self, "estado_widget") and self.estado_widget.winfo_exists():
            color = "#11865B" if self.estado_red.startswith("Conectado con") else ROJO_OSC if self.estado_red == "Desconectado" else GRIS
            self.estado_widget.configure(text=self.estado_red, text_color=color)

    def dibujar_chat(self):
        if hasattr(self, "chat") and self.chat.winfo_exists():
            self.chat.configure(state="normal")
            self.chat.delete("1.0", "end")
            self.chat.insert("end", "\n\n".join(self.historial))
            self.chat.see("end")
            self.chat.configure(state="disabled")

    def procesar_red(self):
        try:
            while True:
                tipo, texto = self.red.eventos.get_nowait()
                if tipo == "estado":
                    self.estado_red = texto
                    self.actualizar_estado()
                elif tipo == "mensaje":
                    self.historial.append(texto)
                    self.dibujar_chat()
                elif tipo == "error" and self.social.sesion:
                    messagebox.showerror("Red local", texto, parent=self)
        except Empty:
            pass
        self.after(100, self.procesar_red)

    def salir_sesion(self):
        self.red.cerrar()
        self.social.cerrar_sesion()
        self.historial.clear()
        while not self.red.eventos.empty():
            self.red.eventos.get_nowait()
        self.estado_red = "Desconectado"
        self.mostrar_login()

    def cerrar(self):
        self.red.cerrar()
        self.social.cerrar_sesion()
        # Cancelar callbacks pendientes antes de destruir la ventana.
        for temporizador in self.tk.call("after", "info"):
            self.tk.call("after", "cancel", temporizador)
        self.destroy()