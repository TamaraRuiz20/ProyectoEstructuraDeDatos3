# Social UNA · Red Social Estudiantil

Aplicación de escritorio para Estructuras de Datos. Permite registrar estudiantes, iniciar sesión, buscar personas, agregar amigos y compartir publicaciones. Incluye un chat de texto TCP para dos computadoras en una red local. No utiliza bases de datos, servidor web ni frameworks web.

## Integrantes

- Tamara
- Amanda
- Jeff
- Allison

## Tecnologías y requisitos

Python 3.10 o superior, Tkinter, CustomTkinter y biblioteca estándar (`json`, `socket`, `threading`, `queue`, `hashlib`). Probado aquí con Python 3.12 y CustomTkinter 6.0.0. Se recomienda Python 3.13 para trabajar en PyCharm. Necesita un escritorio gráfico.

## Instalar y ejecutar en Windows

1. Extraer **todo** el ZIP en una carpeta con permisos de escritura.
2. Abrir esa carpeta en PyCharm o en una terminal.
3. Crear y activar el entorno e instalar dependencias:

```powershell
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

Si PowerShell bloquea la activación, se puede ejecutar directamente:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe main.py
```

En PyCharm: abrir SocialUNA como proyecto, seleccionar el intérprete del entorno, instalar requirements.txt y ejecutar main.py. La interacción con la aplicación es enteramente gráfica; la terminal solo se usa para instalación y pruebas.

En Linux/macOS: `python3 -m venv .venv`, `source .venv/bin/activate`, `python -m pip install -r requirements.txt`, `python main.py`. Algunas instalaciones de Linux necesitan el paquete del sistema `python3-tk`.

## Cuentas de demostración

| Nombre | Usuario | Contraseña |
| --- | --- | --- |
| Tamara | tamara | una123 |
| Amanda | amanda | una123 |
| Jeff | jeff | una123 |
| Allison | allison | una123 |

Son cuentas ficticias de demostración. Todas tienen la misma contraseña para facilitar la presentación. Los JSON contienen hashes y sales diferentes, nunca las contraseñas originales.

## Recorrido de la aplicación

- **Inicio:** publicaciones propias y de amigos, de más recientes a más antiguas.
- **Amigos:** lista de vecinos del usuario en el grafo.
- **Buscar:** búsqueda parcial por nombre o usuario; permite agregar amigos inmediatamente, sin solicitudes pendientes. Impide duplicados y agregarse a uno mismo.
- **Publicar:** texto de 1 a 2000 caracteres.
- **Red local:** iniciar servidor, conectarse manualmente por IP, enviar/recibir texto y desconectarse.
- **Perfil:** datos del estudiante y sus publicaciones.
- **Cerrar sesión:** termina también la conexión de red y limpia el chat de la sesión.

El registro exige nombre de 2–80 caracteres, usuario de 3–24 letras ASCII minúsculas/números/guion bajo y contraseña de 6–128 caracteres. Los usuarios se normalizan a minúsculas.

## Organización

```text
SocialUNA/
  main.py                    Punto de entrada
  models/                    Usuario y Publicacion (clases de datos)
  structures/                GrafoAmistades
  services/social.py         Registro, login, búsqueda, amigos y publicaciones
  persistence/archivos.py    Lectura y guardado JSON
  network/                   Servidor, cliente y conexión TCP
  gui/app.py                 Pantallas de la aplicación
  logs/auditoria.py          Función central de auditoría
  data/                      Tres JSON con los datos de demostración
  tests/                     Pruebas de lógica, TCP y GUI
  README.md
  GUIA_DEFENSA.md
  PRUEBAS.md
  requirements.txt
```

Las pantallas están juntas en una sola clase de GUI, y las operaciones en un solo servicio, para evitar archivos repetitivos y una arquitectura demasiado grande.

## Estructuras y persistencia

Al iniciar, `Social` lee una sola vez los tres JSON y reconstruye:

| Información | Estructura en memoria | Archivo |
| --- | --- | --- |
| Estudiantes | Diccionario `id -> Usuario` | data/usuarios.json |
| Publicaciones | Lista de objetos Publicacion | data/publicaciones.json |
| Amistades | Diccionario `id -> set(ids amigos)` | data/amistades.json |

Durante la sesión, búsquedas, login y feed trabajan en memoria. Al registrar, publicar o agregar un amigo se guarda únicamente el JSON correspondiente. Se escribe primero un temporal y se reemplaza el original, evitando dejar un JSON incompleto. Si falla la escritura se revierte la operación en memoria. Las rutas dependen de la ubicación de main.py, no de la carpeta desde donde se ejecuta.

Si no existen los archivos se crean vacíos; la copia entregada incluye los datos de prueba. No se vuelven a insertar ejemplos al borrar datos. Un JSON dañado se informa mediante una alerta y se conserva para revisarlo. Para respaldar información basta copiar data/. Solo debe abrirse **una instancia por carpeta de datos**; dos computadoras deben usar copias independientes.

### Grafo de amistades

Es un grafo no dirigido sin pesos. Para agregar A–B se inserta B en el conjunto de A y A en el de B. Los conjuntos son la representación de las listas de adyacencia que impide repetir vecinos. En JSON se convierten a listas, porque JSON no admite conjuntos.

Ejemplos iniciales: Tamara–Amanda, Tamara–Jeff, Jeff–Allison. El feed toma `{usuario actual} unión amigos`, filtra las publicaciones por esos autores y ordena por fecha/hora descendente (ID como desempate).

### Contraseñas

`hashlib.pbkdf2_hmac` calcula el hash con SHA-256, una sal aleatoria por usuario y 120000 iteraciones. Al iniciar sesión se repite el cálculo y se compara con `hmac.compare_digest`. La contraseña se oculta en los campos y no se escribe en logs. Es un mecanismo pequeño basado en funciones estándar.

## Red local: demostración en dos computadoras

1. Conectar ambas a la misma LAN (Wi-Fi o cable) y abrir una copia del proyecto en cada una.
2. Iniciar sesión y abrir **Red local** en ambas.
3. En la computadora A seleccionar puerto **5000** y pulsar **Iniciar servidor**. Aparece “Esperando conexión”.
4. En B ingresar la **IP local de A**, el mismo puerto, y pulsar **Conectar**. La IP mostrada es orientativa: si hay varias interfaces/VPN confirmar la dirección LAN con `ipconfig` en Windows.
5. Cuando ambas indiquen **Conectado**, escribir y enviar mensajes desde cualquiera.
6. Pulsar **Desconectar**, cerrar sesión o cerrar la ventana para terminar. Para otra conversación, iniciar de nuevo el servidor y conectar el cliente.

Permitir Python en el firewall de Windows para redes privadas. Si no conecta, revisar IP, puerto, firewall y que el router no tenga aislamiento de clientes/red de invitados. No hay descubrimiento automático, voz, video ni archivos.

Para probar en una sola computadora, extraer dos copias en carpetas distintas. A inicia el servidor y B conecta a `127.0.0.1`. La prueba automatizada de TCP usa esta dirección.

TCP transporta bytes, no mensajes completos. Cada mensaje es un objeto JSON con autor/texto, codificado UTF-8 y terminado en salto de línea. El receptor acumula fragmentos y separa las tramas completas; así soporta tildes, emojis, saltos de línea dentro del texto y varios mensajes en una recepción. Se limitan los tamaños de mensaje/trama. Un hilo recibe, otro acepta/conecta y los envíos se hacen fuera de la GUI. Una cola lleva los eventos a `after`, que actualiza los widgets en el hilo principal.

La red conecta un par de computadoras. Los usuarios, amistades y publicaciones de cada copia **son locales y no se sincronizan**. Los mensajes de chat solo permanecen durante la sesión, no se guardan como publicaciones. El chat es una demostración en una LAN de confianza: no cifra el tráfico ni verifica la identidad remota; el autor es el nombre enviado por el otro equipo.

## Auditoría

`Auditoria.registrar(accion, detalle)` agrega líneas a `logs/social_una.log` con modo append y un cerrojo para los hilos. Registra registro, login correcto/fallido, amistad, publicación, servidor, conexión, envío, recepción y cierre. Los mensajes privados no se copian al log. El archivo se crea con la primera acción y .gitignore evita subirlo a GitHub.

```text
[2026-11-03 10:20:30] LOGIN | Usuario: tamara
[2026-11-03 10:21:10] AMISTAD | tamara -> allison
```

## Pruebas

```powershell
python -m unittest discover -v
python -m tests.prueba_gui
```

Las pruebas usan carpetas temporales y no alteran los ejemplos. La prueba GUI necesita una pantalla gráfica y abre/cierra ventanas automáticamente. Ver PRUEBAS.md para alcance y resultados.

## GitHub

Crear un repositorio vacío y subir esta carpeta. No se ha publicado automáticamente en ninguna cuenta. `.gitignore` excluye entornos, cachés y logs; los JSON de demostración se incluyen para ejecutar inmediatamente. Si se usan datos reales, revisar los JSON antes de subirlos.
