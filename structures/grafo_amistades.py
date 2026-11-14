class GrafoAmistades:
    """Grafo no dirigido: cada ID tiene un conjunto de vecinos sin duplicados."""
    def __init__(self, datos=None):
        self.adyacencia = {int(k): set(v) for k, v in (datos or {}).items()}

    def agregar_usuario(self, identificador):
        self.adyacencia.setdefault(identificador, set())

    def agregar(self, origen, destino):
        if origen == destino:
            raise ValueError("No puedes agregarte a ti mismo.")
        self.agregar_usuario(origen)
        self.agregar_usuario(destino)
        if destino in self.adyacencia[origen]:
            raise ValueError("Este estudiante ya es tu amigo.")
        self.adyacencia[origen].add(destino)
        self.adyacencia[destino].add(origen)

    def amigos(self, identificador):
        return set(self.adyacencia.get(identificador, set()))

    def a_dict(self):
        return {str(k): sorted(v) for k, v in self.adyacencia.items()}
