# Guía breve para defender Social UNA

## Explicación de un minuto

“Social UNA es una aplicación de escritorio en Python con CustomTkinter. Al iniciar reconstruye usuarios, publicaciones y amistades desde archivos JSON. Los usuarios se guardan en un diccionario, las publicaciones en una lista dinámica y las amistades en un grafo no dirigido mediante conjuntos de adyacencia. Las operaciones se realizan en memoria y cada cambio se persiste. El muro filtra los autores que son el usuario o sus amigos y ordena sus publicaciones por fecha. Incluimos un chat TCP de texto para dos computadoras y logs que registran las acciones principales.”

## Dónde mostrar cada parte

| Tema | Archivo / método | Idea para explicar |
| --- | --- | --- |
| Carga inicial | services/social.py, __init__ | JSON -> objetos y estructuras |
| Registro | Social.registrar | Validación, ID, hash, guardar |
| Login | Social.login | Busca usuario, compara hash |
| Grafo | structures/grafo_amistades.py | Dos inserciones para una arista |
| Muro | Social.feed | Filtrar autores y ordenar |
| Guardado | persistence/archivos.py | Temporal y reemplazo |
| Auditoría | logs/auditoria.py | Append, fecha y acción |
| Red | network/connection.py | TCP, hilos y cola |
| Interfaz | gui/app.py | Ventanas y navegación |

## Preguntas comunes

**¿Por qué un diccionario para usuarios?** Permite obtener un usuario por ID en tiempo promedio O(1). En esta versión, buscar por nombre/usuario recorre todos los usuarios: O(U). No se mantiene otro índice para conservar la sencillez.

**¿Por qué una lista para publicaciones?** Crece dinámicamente y permite recorrer los textos para construir el muro. Agregar es O(1) amortizado en memoria; guardar el JSON recorre todas las publicaciones.

**¿Por qué un grafo?** Una persona puede tener muchos amigos y cada amistad une dos usuarios. Una lista simple de usuarios no describe esas relaciones.

**¿Es dirigido?** No. A amigo de B implica B amigo de A. No hay solicitudes pendientes.

**¿Por qué sets en las adyacencias?** Evitan duplicados y permiten comprobar una amistad en O(1) promedio. Se convierten a listas al guardar.

**¿Cuánto cuesta el feed?** Se recorren P publicaciones y se ordenan K visibles: aproximadamente O(P + K log K), además de obtener los amigos.

**¿Dónde hay recursividad o estructuras propias de nodos?** No se requieren para este enunciado. El grafo está implementado con diccionarios y conjuntos de Python, sin librerías de grafos.

**¿Por qué no leer JSON para cada búsqueda?** Leer disco repetidamente es innecesario. JSON conserva los datos y las estructuras en memoria atienden las operaciones.

**¿Por qué usar hilos?** Esperar una conexión o recibir datos bloquearía la ventana si ocurriera en su hilo principal. Los hilos de red producen eventos en una cola y la GUI los procesa con after.

**¿TCP entrega un mensaje por recv?** No. Puede fragmentar o agrupar datos. Por eso usamos JSON terminado en salto de línea y un búfer de bytes.

**¿El chat comparte la base de usuarios?** No. Cada equipo conserva sus JSON. La red solo transmite texto.

**¿Se guardan las contraseñas?** Se almacena un hash con una sal, no el texto original. Para verificar se vuelve a calcular el hash.

## Recorrido sugerido de 5 minutos

1. Entrar con tamara / una123; enseñar las publicaciones del círculo.
2. Buscar allison, agregarla y volver a Inicio: su publicación pasa a ser visible.
3. Crear una publicación, verla en Inicio y Perfil.
4. Cerrar y abrir para demostrar persistencia; mostrar los tres JSON y el log.
5. En dos copias, iniciar servidor en una y conectar desde la otra; intercambiar texto.
6. Mostrar GrafoAmistades.agregar y Social.feed para explicar las estructuras.

La primera demostración modifica los ejemplos. Para repetirla desde cero, extraer otra copia del ZIP.
