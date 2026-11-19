import heapq


def dijkstra(rede, origem, destino):
    """Encontra o caminho de menor distancia entre origem e destino.

    Argumentos:
        rede (Rede): rede a percorrer. Nao e alterada.
        origem (str): ID do ponto de partida.
        destino (str): ID do ponto de chegada.

    Retorna:
        tuple[list[str], float | None]:
            - ([caminho], distancia) se houver caminho.
            - ([], None) se nao houver caminho.
            - ([origem], 0) se origem for igual ao destino.

    Levanta:
        ValueError: se origem ou destino nao existirem na rede.
    """
    if origem not in rede.vertices:
        raise ValueError(f"Origem {origem!r} nao existe na rede.")
    if destino not in rede.vertices:
        raise ValueError(f"Destino {destino!r} nao existe na rede.")

    if origem == destino:
        return ([origem], 0)

    # Fila de prioridade com (distancia_acumulada, no_atual, caminho_ate_aqui)
    fila = [(0, origem, [origem])]
    visitados = set()

    while fila:
        dist, atual, caminho = heapq.heappop(fila)
        if atual in visitados:
            continue
        visitados.add(atual)

        if atual == destino:
            return (caminho, dist)

        for vizinho, d in rede.vizinhos_ativos(atual):
            if vizinho not in visitados:
                heapq.heappush(fila, (dist + d, vizinho, caminho + [vizinho]))

    return ([], None)
