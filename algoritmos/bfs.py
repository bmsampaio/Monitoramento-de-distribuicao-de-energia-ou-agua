"""Busca em largura (BFS) sobre as tubulações ativas da rede.

Responde: "a partir do reservatório, quais pontos ainda recebem água?", ou
seja, quais pontos estão ligados à origem só por tubulações ativas.

Ideia: visitar a rede em camadas (a origem, depois os vizinhos dela, depois
os vizinhos desses, ...) usando uma fila. As distâncias em km são
ignoradas; o menor caminho é papel do Dijkstra.

Complexidade (V = pontos, E = tubulações, inclusive inativas):
    Tempo O(V + E): cada ponto entra na fila uma vez e cada tubulação é
    vista duas vezes, uma por extremo. As inativas também contam, porque
    rede.vizinhos_ativos olha cada uma para descartá-la.
    Espaço O(V): visitados, fila e resultado guardam cada ponto uma vez.

Premissas:
    - Só tubulações ativas (o filtro é feito por rede.vizinhos_ativos).
    - A rede recebida não é alterada.
    - Grafo não direcionado, sem laços nem tubulações duplicadas.

Uso no projeto: a simulação de falhas (servicos/simulacao.py) roda a BFS a
partir do reservatório antes e depois de desativar uma tubulação; os pontos
que somem do resultado perderam o abastecimento. Os testes de pontes também
a usam para contar componentes.
"""

from collections import deque


def bfs(rede, origem):
    """Lista os pontos alcançáveis a partir de origem por tubulações ativas.

    Pontos que não aparecem no resultado estão desligados da origem.

    Args:
        rede (Rede): rede a percorrer. Não é alterada.
        origem (str): ID do ponto de partida, por exemplo "R".

    Returns:
        list[str]: IDs alcançáveis, sem repetição, na ordem de visita: a
        origem primeiro, depois os pontos a 1 tubulação dela, depois a 2, e
        assim por diante. Dentro de uma camada, a ordem segue o cadastro.

    Raises:
        ValueError: se origem não existe na rede.

    Complexidade:
        Tempo O(V + E), espaço O(V).

    Exemplo:
        Na rede de exemplo (testes/auxiliares.criar_rede_exemplo)::

            bfs(rede, "R")   # ['R', 'A', 'B', 'C', 'D', 'E', 'F', 'G']
            copia = rede.copiar()
            copia.alterar_estado("T01", False)   # desativa R-A
            bfs(copia, "R")  # ['R']
    """
    # Validar aqui dá uma mensagem mais clara que o erro genérico da Rede.
    if origem not in rede.vertices:
        raise ValueError(f"O ponto de origem {origem!r} não existe na rede.")

    # O ponto é marcado ao ENTRAR na fila, não ao sair. Assim ninguém é
    # enfileirado duas vezes: na rede de exemplo, B e C enfileirariam D cada
    # um, e D sairia repetido no resultado.
    visitados = {origem}
    fila = deque([origem])  # popleft é O(1); list.pop(0) seria O(V)
    ordem_de_visita = []

    while fila:
        # Fila FIFO: os pontos saem na ordem em que entraram, camada por
        # camada, então esta lista já é a ordem de visita.
        ponto = fila.popleft()
        ordem_de_visita.append(ponto)

        for vizinho, _distancia in rede.vizinhos_ativos(ponto):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(vizinho)

    return ordem_de_visita
