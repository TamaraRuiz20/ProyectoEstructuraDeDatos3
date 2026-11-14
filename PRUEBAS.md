# Verificación de Social UNA

Fecha: 3 de noviembre de 2026.
Entorno: Python 3.12, CustomTkinter 6.0.0, Linux y pantalla virtual Xvfb.

## Resultados ejecutados

| Comprobación | Resultado |
| --- | --- |
| Compilación de módulos Python | Correcta |
| Registro, normalización, duplicados, validación y login fallido/correcto | Correcta |
| Contraseñas ausentes en texto plano y sales diferentes | Correcta |
| Grafo simétrico; rechaza amistad propia, repetida y destino inexistente | Correcta |
| Feed propio/amigos, exclusión de terceros y orden cronológico | Correcta |
| Reconstrucción desde JSON en una nueva instancia | Correcta |
| Logs conservan registro, login, amistad, publicación y logout | Correcta |
| Fallo de escritura revierte cambios en memoria | Correcta |
| JSON con sintaxis dañada se conserva y reporta error | Correcta |
| TCP entre dos objetos independientes por 127.0.0.1, en ambos sentidos | Correcta |
| Unicode, emojis, salto de línea y cierre remoto | Correcta |
| TCP con tramas fragmentadas y concatenadas | Correcta |
| GUI: registro, login, buscar, agregar, publicar, feed, amigos, perfil y red local | Correcta |
| GUI: cerrar y crear otra ventana/servicio; datos conservados | Correcta |
| Ejecución real de main.py con cierre programado de prueba | Correcta |

Se ejecutaron **6 pruebas unitarias/de integración** con `python -m unittest discover -v`, más el recorrido gráfico `python -m tests.prueba_gui`. La prueba gráfica pulsa botones e ingresa valores en widgets reales, sustituye únicamente los diálogos modales por verificaciones y comprueba que no aparezcan errores. Las pruebas funcionales utilizan carpetas temporales independientes de los datos de demostración.

Se revisaron visualmente login, feed y red local en pantalla virtual. Durante la revisión se corrigió una actualización repetida del ajuste de texto y se verificó nuevamente el cierre de las ventanas. La apariencia final de fuentes y bordes depende del sistema gráfico; el código usa Segoe UI en Windows.

## Alcance pendiente en equipos físicos

No se dispuso de dos computadoras físicas en la misma LAN. Se comprobó la conexión TCP real por loopback, no el firewall ni el router de ustedes. El README explica cómo hacer esa demostración. Tampoco se ejecutó directamente en Windows en este entorno.

## Comprobación manual en su equipo

1. Entrar con tamara / una123: debe ver las publicaciones de Tamara, Amanda y Jeff, pero no la de Allison.
2. Buscar allison y agregarla. Volver a Inicio: ahora aparece su publicación.
3. Publicar un texto y comprobarlo en Inicio y Perfil.
4. Intentar publicar solo espacios: debe aparecer una alerta.
5. Cerrar y abrir; comprobar amigos y publicaciones conservados.
6. Registrar otro usuario; intentar repetirlo y probar una clave incorrecta.
7. Abrir logs/social_una.log y comprobar que se agregaron líneas.
8. En dos copias, iniciar servidor en A y conectar B. Enviar texto desde ambas; desconectar y reconectar.

No ejecutar dos instancias contra la misma carpeta de datos. Para repetir desde el estado inicial extraer nuevamente el ZIP en una carpeta nueva.
