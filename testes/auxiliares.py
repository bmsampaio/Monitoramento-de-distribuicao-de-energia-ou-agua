"""Funções de apoio compartilhadas pelos testes.

A rede de exemplo vem de exemplos/rede_exemplo.py, a mesma usada pela
interface. As demais redes de teste são montadas aqui.
"""

from exemplos.rede_exemplo import criar_rede_exemplo  # noqa: F401 (reexportada)
from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao


def montar_rede(pontos, tubulacoes):
    """Monta uma Rede com os pontos e as tubulações informados, todos ativos.

    Args:
        pontos (list[str]): IDs dos pontos, na ordem de cadastro.
        tubulacoes (list[tuple]): tuplas (id, origem, destino, distancia),
            na ordem de cadastro. Para desativar uma tubulação, usar
            rede.alterar_estado(id, False) depois de montar a rede.

    Returns:
        Rede: rede nova, independente de qualquer outra.
    """
    rede = Rede()
    for ponto in pontos:
        rede.adicionar_no(No(ponto, f"Ponto {ponto}", "ponto_demanda"))
    for identificador, origem, destino, distancia in tubulacoes:
        rede.adicionar_tubulacao(
            Tubulacao(identificador, origem, destino, distancia)
        )
    return rede


def rede_por_pares(texto):
    """Monta uma rede a partir de um texto como "A-B B-C C-A".

    Serve para escrever redes de teste pequenas em uma linha. Cada par
    "X-Y" vira uma tubulação ativa de 1 km entre X e Y, com IDs T01, T02,
    ... na ordem em que os pares aparecem no texto. Os pontos são
    cadastrados na ordem em que aparecem pela primeira vez. A distância é
    sempre 1 porque BFS e pontes não usam distâncias.

    Args:
        texto (str): pares separados por espaço; cada par tem os IDs dos
            dois pontos separados por hífen.

    Returns:
        Rede: rede nova com os pontos e tubulações descritos.

    Exemplo:
        rede_por_pares("A-B B-C") cria os pontos A, B e C e as tubulações
        T01 (A-B) e T02 (B-C).
    """
    pares = [par.split("-") for par in texto.split()]
    pontos = []
    for par in pares:
        for ponto in par:
            if ponto not in pontos:
                pontos.append(ponto)
    tubulacoes = [
        (f"T{indice:02d}", origem, destino, 1)
        for indice, (origem, destino) in enumerate(pares, start=1)
    ]
    return montar_rede(pontos, tubulacoes)


def retrato_da_rede(rede):
    """Resume todo o estado da rede em uma estrutura comparável com ==.

    Usado nos testes que verificam que um algoritmo não altera a rede: tira-se
    um retrato antes e outro depois de chamar o algoritmo e compara-se os
    dois. Inclui os pontos, todos os campos de cada tubulação (inclusive
    ativa) e a adjacência.

    Args:
        rede (Rede): rede a ser resumida. Não é alterada.

    Returns:
        tuple: (pontos, tubulacoes, adjacencia), em que pontos mapeia ID para
        (nome, tipo), tubulacoes mapeia ID para (origem, destino, distancia,
        ativa) e adjacencia é uma cópia de rede.adjacencia.
    """
    pontos = {
        identificador: (no.nome, no.tipo)
        for identificador, no in rede.vertices.items()
    }
    tubulacoes = {
        identificador: (t.origem, t.destino, t.distancia, t.ativa)
        for identificador, t in rede.tubulacoes.items()
    }
    adjacencia = {
        ponto: dict(vizinhos) for ponto, vizinhos in rede.adjacencia.items()
    }
    return pontos, tubulacoes, adjacencia
