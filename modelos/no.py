class No:
    """Representa um ponto da rede (reservatorio ou ponto de demanda).

    Parametros:
        identificador (str): ID unico do no, ex: "R" ou "1".
        nome (str): nome descritivo do ponto.
        tipo (str): categoria, ex: "reservatorio" ou "ponto_demanda".
    """

    def __init__(self, identificador, nome, tipo):
        self.identificador = identificador
        self.nome = nome
        self.tipo = tipo
