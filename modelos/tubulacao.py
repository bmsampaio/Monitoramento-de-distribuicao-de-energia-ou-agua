class Tubulacao:
    """Representa uma tubulacao entre dois nos da rede.

    Parametros:
        identificador (str): ID unico da tubulacao, ex: "T1".
        origem (str): ID de uma extremidade.
        destino (str): ID da outra extremidade.
        distancia (float): distancia em quilometros.
        ativa (bool): True se a tubulacao esta ativa, False se desativada.
    """

    def __init__(self, identificador, origem, destino, distancia, ativa=True):
        self.identificador = identificador
        self.origem = origem
        self.destino = destino
        self.distancia = distancia
        self.ativa = ativa
