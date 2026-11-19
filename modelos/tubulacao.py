class Tubulacao:
    def __init__(self, identificador, origem, destino, distancia, ativa=True):
        self.identificador = identificador
        self.origem = origem
        self.destino = destino
        self.distancia = distancia
        self.ativa = ativa