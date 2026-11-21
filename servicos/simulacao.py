"""Simulacao de falhas na rede de distribuicao de agua.

Compara o comportamento da rede antes e depois da interrupcao de uma ou
mais tubulacoes, usando BFS, Dijkstra e identificacao de pontes.

A rede original nunca e alterada. As falhas sao aplicadas em uma copia
obtida por rede.copiar(), e o "antes" e sempre a rede original.
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
            - "alcancaveis" (list[str]): nos alcancaveis a partir da origem.
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
        "alcancaveis": alcancaveis,
        "caminho": caminho,
        "distancia": distancia,
        "pontes": pontes,
    }


def simular_falha(rede, origem, destino, tubulacao_id):
    """Simula a interrupcao de uma tubulacao e compara antes/depois.

    Atalho para simular_falhas com uma tubulacao so.

    Argumentos:
        rede (Rede): rede original. Nao e modificada.
        origem (str): ID do ponto de origem.
        destino (str): ID do ponto de destino.
        tubulacao_id (str | None): ID da tubulacao a interromper.
            Se None, nao aplica falha.

    Retorna:
        dict de simular_falhas, mais a chave "tubulacao_interrompida"
        (str | None) com o ID recebido.

    Levanta:
        ValueError: se origem/destino nao existirem ou tubulacao_id for invalida.
    """
    ids = [] if tubulacao_id is None else [tubulacao_id]
    resultado = simular_falhas(rede, origem, destino, ids)
    resultado["tubulacao_interrompida"] = tubulacao_id
    return resultado


def simular_falhas(rede, origem, destino, tubulacoes_ids):
    """Simula a interrupcao de varias tubulacoes ao mesmo tempo e compara antes/depois.

    Fluxo:
    1. Calcula indicadores da rede ORIGINAL (antes das falhas).
    2. Cria uma copia independente da rede (rede.copiar()).
    3. Desativa todas as tubulacoes informadas na copia.
    4. Recalcula indicadores na copia (depois das falhas).
    5. Compara os dois cenarios.

    Argumentos:
        rede (Rede): rede original. Nao e modificada.
        origem (str): ID do ponto de origem.
        destino (str): ID do ponto de destino.
        tubulacoes_ids (list[str]): IDs das tubulacoes a interromper. IDs
            repetidos contam uma vez. Lista vazia nao aplica falha.

    Retorna:
        dict com a comparacao organizada:
        - "origem" (str): id da origem.
        - "destino" (str): id do destino.
        - "tubulacoes_interrompidas" (list[str]): ids desativados, sem repeticao.
        - "antes" (dict): indicadores da rede original.
        - "depois" (dict): indicadores apos as falhas (igual ao antes sem falha).
        - "caminho_antes" (list[str] | None): caminho minimo antes.
        - "caminho_depois" (list[str] | None): caminho minimo depois.
        - "distancia_antes" (float | None): distancia antes.
        - "distancia_depois" (float | None): distancia depois.
        - "pontes_antes" (list[str]): ids de pontes antes.
        - "pontes_depois" (list[str]): ids de pontes depois.
        - "inacessiveis_apos_falha" (list[str]): nos que ficaram inacessiveis,
          na ordem de visita da BFS.
        - "novas_pontes" (list[str]): tubulacoes que se tornaram pontes.
        - "pontes_nao_sao_mais" (list[str]): tubulacoes que deixaram de ser pontes.
        - "falha_aplicada" (bool): True se alguma tubulacao foi desativada.

    Levanta:
        ValueError: se origem/destino nao existirem ou algum id for invalido.
        TypeError: se tubulacoes_ids for um texto em vez de uma lista.
    """
    if origem not in rede.vertices:
        raise ValueError(f"Origem {origem!r} nao existe na rede.")
    if destino not in rede.vertices:
        raise ValueError(f"Destino {destino!r} nao existe na rede.")
    # Um texto seria percorrido letra por letra ("T04" -> "T", "0", "4").
    if isinstance(tubulacoes_ids, str):
        raise TypeError(
            "tubulacoes_ids deve ser uma lista de IDs; para uma tubulacao, "
            "use simular_falha."
        )

    # Remove repetidos mantendo a ordem em que foram escolhidos.
    tubulacoes_ids = list(dict.fromkeys(tubulacoes_ids))
    inexistentes = [t for t in tubulacoes_ids if t not in rede.tubulacoes]
    if inexistentes:
        nomes = ", ".join(repr(t) for t in inexistentes)
        raise ValueError(f"Tubulacao(oes) {nomes} nao existe(m) na rede.")

    # Cenario antes das falhas (rede original, sem alteracoes)
    antes = indicadores(rede, origem, destino)

    # Valores default do cenario depois
    depois = None
    caminho_depois = None
    distancia_depois = None
    pontes_depois = None
    inacessiveis_apos_falha = []
    novas_pontes = []
    pontes_nao_sao_mais = []
    falha_aplicada = bool(tubulacoes_ids)

    if falha_aplicada:
        # Copia independente para aplicar as falhas sem estragar a original
        rede_com_falha = rede.copiar()
        for tubulacao_id in tubulacoes_ids:
            rede_com_falha.alterar_estado(tubulacao_id, False)

        # Cenario depois das falhas
        depois = indicadores(rede_com_falha, origem, destino)
        caminho_depois = depois["caminho"]
        distancia_depois = depois["distancia"]
        pontes_depois = depois["pontes"]

        # Nos que ficaram inacessiveis (eram alcancaveis antes, nao estao depois),
        # na ordem de visita da BFS: sorted() poria "10" antes de "2" na R-9.
        depois_set = set(depois["alcancaveis"])
        inacessiveis_apos_falha = [
            p for p in antes["alcancaveis"] if p not in depois_set
        ]

        # Comparacao de pontes
        antes_pontes = set(antes["pontes"])
        depois_pontes = set(depois["pontes"])
        novas_pontes = sorted(depois_pontes - antes_pontes)
        pontes_nao_sao_mais = sorted(antes_pontes - depois_pontes)
    else:
        # Sem falha: depois espelha o antes
        depois = {
            "alcancaveis": list(antes["alcancaveis"]),
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
        "tubulacoes_interrompidas": tubulacoes_ids,
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
