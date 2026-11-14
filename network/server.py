import socket

def abrir_servidor(puerto, host="0.0.0.0"):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        servidor.bind((host, puerto))
        servidor.listen(1)
        servidor.settimeout(0.5)
        return servidor
    except OSError:
        servidor.close()
        raise
