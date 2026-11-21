"""Menor caminho entre dois pontos com o algoritmo de Dijkstra.

Responde: "qual a rota mais curta, em km, entre a origem e o destino?".
O peso de cada tubulação é a distância.

Ideia: uma fila de prioridade (heapq) entrega sempre o ponto com a menor
distância acumulada. Cada ponto guarda o anterior na melhor rota conhecida,
e o caminho é reconstruído do destino até a origem.

Complexidade (V = pontos, E = tubulações):
    Tempo O((V + E) log V): cada tubulação pode inserir uma entrada na fila,
    e cada operação na fila custa O(log V).
    Espaço O(V + E): distâncias e anteriores por ponto, fila com até E itens.

Premissas:
    - Só tubulações ativas (o filtro é feito por rede.vizinhos_ativos).
    - A rede recebida não é alterada.
    - Distâncias não negativas (a Rede já rejeita distância <= 0).

Uso no projeto: a simulação de falhas (servicos/simulacao.py) calcula a rota
antes e depois de desativar uma tubulação.
"""

import heapq
from math import inf


def dijkstra(rede, origem, destino):
    """Calcula o menor caminho de origem até destino por tubulações ativas.

    Args:
        rede (Rede): rede a percorrer. Não é alterada.
        origem (str): ID do ponto de partida.
        destino (str): ID do ponto de chegada.

    Returns:
        tuple[list[str], float | None]: (caminho, distância total em km).
        Sem caminho: ([], None). Origem igual ao destino: ([origem], 0).
        Com duas rotas de mesma distância, devolve uma delas.

    Raises:
        ValueError: se origem ou destino não existem na rede, ou se houver
        distância negativa.

    Complexidade:
        Tempo O((V + E) log V), espaço O(V + E).

    Exemplo:
        Na rede de exemplo (exemplos/rede_exemplo.py)::

            dijkstra(rede, "R", "G")  # (['R', 'A', 'B', 'D', 'F', 'G'], 10)
    """
    if origem not in rede.vertices:
        raise ValueError(f"O ponto de origem {origem!r} não existe na rede.")
    if destino not in rede.vertices:
        raise ValueError(f"O ponto de destino {destino!r} não existe na rede.")

    # Menor distância conhecida até cada ponto e o ponto anterior nessa rota.
    distancias = {origem: 0}
    anteriores = {}
    fila = [(0, origem)]

    while fila:
        distancia_atual, atual = heapq.heappop(fila)

        # Entrada antiga: o ponto já foi alcançado por uma distância menor.
        if distancia_atual > distancias[atual]:
            continue

        # Quando o destino sai da fila, sua distância já é a mínima.
        if atual == destino:
            break

        for vizinho, peso in rede.vizinhos_ativos(atual):
            if peso < 0:
                raise ValueError("Peso negativo não permitido.")

            nova_distancia = distancia_atual + peso
            if nova_distancia < distancias.get(vizinho, inf):
                distancias[vizinho] = nova_distancia
                anteriores[vizinho] = atual
                heapq.heappush(fila, (nova_distancia, vizinho))

    if destino not in distancias:
        return [], None

    caminho = [destino]
    while caminho[-1] != origem:
        caminho.append(anteriores[caminho[-1]])
    caminho.reverse()

    return caminho, distancias[destino]
