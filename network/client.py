import socket

def conectar(ip, puerto):
    socket.inet_pton(socket.AF_INET, ip)
    return socket.create_connection((ip, puerto), timeout=4)

def ip_local():
    # No envía datos: UDP connect permite consultar la interfaz de salida.
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as consulta:
            consulta.connect(("192.0.2.1", 80))
            return consulta.getsockname()[0]
    except OSError:
        return socket.gethostbyname(socket.gethostname())
