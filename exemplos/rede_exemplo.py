"""Rede de exemplo do plano: 8 pontos e 10 tubulações.

Fonte única da rede pequena, usada pela interface e pelos testes. As
tubulações seguem a ordem das conexões no README:

    T01 R-A 2 km    T06 C-D 6 km
    T02 A-B 2 km    T07 C-E 4 km
    T03 A-C 3 km    T08 D-F 2 km
    T04 B-D 2 km    T09 E-F 3 km
    T05 B-E 5 km    T10 F-G 2 km

Resultados esperados: R-A-B-D-F-G com 10 km; sem B-D, 14 km; pontes R-A e F-G.
"""

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao

PONTOS = [
    ("R", "Reservatório principal", "reservatorio"),
    ("A", "Estação de bombeamento", "bombeamento"),
    ("B", "Ponto intermediário B", "intermediario"),
    ("C", "Ponto intermediário C", "intermediario"),
    ("D", "Setor D", "setor"),
    ("E", "Setor E", "setor"),
    ("F", "Setor F", "setor"),
    ("G", "Setor G", "setor"),
]

TUBULACOES = [
    ("T01", "R", "A", 2), ("T02", "A", "B", 2), ("T03", "A", "C", 3),
    ("T04", "B", "D", 2), ("T05", "B", "E", 5), ("T06", "C", "D", 6),
    ("T07", "C", "E", 4), ("T08", "D", "F", 2), ("T09", "E", "F", 3),
    ("T10", "F", "G", 2),
]

# Posições fixas para o desenho, no mesmo formato do plano.
POSICOES = {
    "R": (0.0, 0.5), "A": (0.18, 0.5), "B": (0.4, 0.9), "C": (0.4, 0.1),
    "D": (0.62, 0.9), "E": (0.62, 0.1), "F": (0.82, 0.5), "G": (1.0, 0.5),
}


def criar_rede_exemplo():
    """Monta a rede de exemplo, com todas as tubulações ativas.

    Returns:
        Rede: rede nova a cada chamada, para que uma falha simulada em um
        uso não afete os outros.
    """
    rede = Rede()
    for identificador, nome, tipo in PONTOS:
        rede.adicionar_no(No(identificador, nome, tipo))
    for identificador, origem, destino, distancia in TUBULACOES:
        rede.adicionar_tubulacao(
            Tubulacao(identificador, origem, destino, distancia)
        )
    return rede
