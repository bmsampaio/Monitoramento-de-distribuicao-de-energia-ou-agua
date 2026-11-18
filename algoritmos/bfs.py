from collections import deque


def bfs(rede, origem):
    """Lista os nos alcancaveis a partir da origem por tubulacoes ativas.

    Argumentos:
        rede (Rede): rede a percorrer. Nao e alterada.
        origem (str): ID do ponto de partida, ex: "R".

    Retorna:
        list[str]: IDs alcancaveis, incluindo a origem, em ordem de visita.

    Levanta:
        ValueError: se a origem nao existir na rede.
    """
    if origem not in rede.vertices:
        raise ValueError(f"Origem {origem!r} nao existe na rede.")

    visitados = {origem}
    fila = deque([origem])
    ordem = []

    while fila:
        ponto = fila.popleft()
        ordem.append(ponto)
        for vizinho, _dist in rede.vizinhos_ativos(ponto):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

    return ordem
