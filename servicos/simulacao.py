"""Simulacao de falhas na rede de distribuicao de agua.

Compara o comportamento da rede antes e depois da interrupcao de uma
tubulacao, usando BFS, Dijkstra e identificacao de pontes.

A rede original nunca e alterada. A falha e aplicada em uma copia
obtida por rede.copiar().
"""

from algoritmos.bfs import bfs
from algoritmos.dijkstra import dijkstra
from algoritmos.pontes import encontrar_pontes


def indicadores(rede, origem, destino):
    """Calcula os indicadores de conectividade para um cenario.

    Argumentos:
        rede (Rede): rede a ser analisada. Nao e alterada.
        origem (str): ID do ponto de origem.
        destino (str): ID do ponto de destino.

    Retorna:
        dict com as chaves:
            - "alcançaveis" (list[str]): nos alcancaveis a partir da origem.
            - "caminho" (list[str] | None): caminho minimo entre origem e destino.
            - "distancia" (float | None): distancia do caminho minimo.
            - "pontes" (list[str]): ids das tubulacoes pontes.

    Levanta:
        ValueError: se origem ou destino nao existirem na rede.
    """
    if origem not in rede.vertices:
        raise ValueError(f"Origem {origem!r} nao existe na rede.")
    if destino not in rede.vertices:
        raise ValueError(f"Destino {destino!r} nao existe na rede.")

    alcancaveis = bfs(rede, origem)
    caminho, distancia = dijkstra(rede, origem, destino)
    pontes = encontrar_pontes(rede)

    # Normaliza: caminho vazio significa sem caminho
    if not caminho:
        caminho = None
        distancia = None

    return {
        "alcançaveis": alcancaveis,
        "caminho": caminho,
        "distancia": distancia,
        "pontes": pontes,
    }


def simular_falha(rede, origem, destino, tubulacao_id):
    """Simula a interrupcao de uma tubulacao e compara antes/depois.

    Fluxo:
    1. Calcula indicadores da rede ORIGINAL (antes da falha).
    2. Cria uma copia independente da rede (rede.copiar()).
    3. Desativa a tubulacao informada na copia.
    4. Recalcula indicadores na copia (depois da falha).
    5. Compara os dois cenarios.

    Argumentos:
        rede (Rede): rede original. Nao e modificada.
        origem (str): ID do ponto de origem.
        destino (str): ID do ponto de destino.
        tubulacao_id (str | None): ID da tubulacao a interromper.
            Se None, nao aplica falha.

    Retorna:
        dict com a comparacao organizada:
        - "origem" (str): id da origem.
        - "destino" (str): id do destino.
        - "tubulacao_interrompida" (str | None): id da tubulacao desativada.
        - "antes" (dict): indicadores da rede original.
        - "depois" (dict | None): indicadores apos a falha (None se nao houver falha).
        - "caminho_antes" (list[str] | None): caminho minimo antes.
        - "caminho_depois" (list[str] | None): caminho minimo depois.
        - "distancia_antes" (float | None): distancia antes.
        - "distancia_depois" (float | None): distancia depois.
        - "pontes_antes" (list[str]): ids de pontes antes.
        - "pontes_depois" (list[str] | None): ids de pontes depois.
        - "inacessiveis_apos_falha" (list[str]): nos que ficaram inacessiveis.
        - "novas_pontes" (list[str]): tubulacoes que se tornaram pontes.
        - "pontes_nao_sao_mais" (list[str]): tubulacoes que deixaram de ser pontes.
        - "falha_aplicada" (bool): True se uma tubulacao foi desativada.

    Levanta:
        ValueError: se origem/destino nao existirem ou tubulacao_id for invalida.
    """
    if origem not in rede.vertices:
        raise ValueError(f"Origem {origem!r} nao existe na rede.")
    if destino not in rede.vertices:
        raise ValueError(f"Destino {destino!r} nao existe na rede.")

    # Cenario antes da falha (rede original, sem alteracoes)
    antes = indicadores(rede, origem, destino)

    # Valores default do cenario depois
    depois = None
    caminho_depois = None
    distancia_depois = None
    pontes_depois = None
    inacessiveis_apos_falha = []
    novas_pontes = []
    pontes_nao_sao_mais = []
    falha_aplicada = False

    if tubulacao_id is not None:
        if tubulacao_id not in rede.tubulacoes:
            raise ValueError(f"Tubulacao {tubulacao_id!r} nao existe na rede.")

        # Copia independente para aplicar a falha sem estragar a original
        rede_com_falha = rede.copiar()
        rede_com_falha.alterar_estado(tubulacao_id, False)
        falha_aplicada = True

        # Cenario depois da falha
        depois = indicadores(rede_com_falha, origem, destino)
        caminho_depois = depois["caminho"]
        distancia_depois = depois["distancia"]
        pontes_depois = depois["pontes"]

        # Nos que ficaram inacessiveis (eram alcancaveis antes, nao estao depois)
        antes_set = set(antes["alcançaveis"])
        depois_set = set(depois["alcançaveis"])
        inacessiveis_apos_falha = sorted(antes_set - depois_set)

        # Comparacao de pontes
        antes_pontes = set(antes["pontes"])
        depois_pontes = set(depois["pontes"])
        novas_pontes = sorted(depois_pontes - antes_pontes)
        pontes_nao_sao_mais = sorted(antes_pontes - depois_pontes)
    else:
        # Sem falha: depois espelha o antes
        depois = {
            "alcançaveis": list(antes["alcançaveis"]),
            "caminho": antes["caminho"],
            "distancia": antes["distancia"],
            "pontes": list(antes["pontes"]),
        }
        caminho_depois = antes["caminho"]
        distancia_depois = antes["distancia"]
        pontes_depois = list(antes["pontes"])

    return {
        "origem": origem,
        "destino": destino,
        "tubulacao_interrompida": tubulacao_id,
        "antes": antes,
        "depois": depois,
        "caminho_antes": antes["caminho"],
        "caminho_depois": caminho_depois,
        "distancia_antes": antes["distancia"],
        "distancia_depois": distancia_depois,
        "pontes_antes": antes["pontes"],
        "pontes_depois": pontes_depois,
        "inacessiveis_apos_falha": inacessiveis_apos_falha,
        "novas_pontes": novas_pontes,
        "pontes_nao_sao_mais": pontes_nao_sao_mais,
        "falha_aplicada": falha_aplicada,
    }
