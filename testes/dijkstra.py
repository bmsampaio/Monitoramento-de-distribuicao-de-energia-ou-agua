import heapq
from math import inf

def dijkstra(rede, origem, destino):

    # Armazena a menor distância conhecida
    distancias = {origem: 0}

    # Guarda o vértice anterior de cada ponto
    anteriores = {}

    # Fila de prioridade: distância, vértice
    fila = [(0, origem)]

    while fila:

        distancia_atual, atual = heapq.heappop(fila)

        # Ignora entradas antigas da fila
        if distancia_atual > distancias.get(atual, inf):
            continue

        # Encontrou o destino
        if atual == destino:
            break

        # Percorre somente tubulações ativas
        for vizinho, peso in rede.vizinhos_ativos(atual):

            if peso < 0:
                raise ValueError("Peso negativo não permitido")

            nova_distancia = distancia_atual + peso

            # Verifica se encontrou um caminho menor
            if nova_distancia < distancias.get(vizinho, inf):

                distancias[vizinho] = nova_distancia
                anteriores[vizinho] = atual

                heapq.heappush(
                    fila,
                    (nova_distancia, vizinho)
                )

    # Caso não exista caminho
    if destino not in distancias:
        return [], None

    # Reconstrói o caminho encontrado
    caminho = [destino]

    while caminho[-1] != origem:
        caminho.append(anteriores[caminho[-1]])

    caminho.reverse()

    return caminho, distancias[destino]
