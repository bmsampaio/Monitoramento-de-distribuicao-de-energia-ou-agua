"""Busca de pontes (tubulações críticas) com o algoritmo de Tarjan.

Responde: "quais tubulações, se falharem sozinhas, dividem a rede?". Uma
ponte é uma tubulação ativa cuja retirada aumenta o número de componentes
conexas. Na rede de exemplo, as pontes são R-A e F-G.

Ideia: uma busca em profundidade (DFS) dá a cada ponto um tempo de
descoberta e um valor low (o menor tempo de descoberta que ele e os pontos
abaixo dele na árvore da busca alcançam com no máximo uma tubulação de
retorno). A tubulação pai-filho é ponte quando low[filho] > descoberta[pai].
A busca usa pilha explícita em vez de recursão, porque redes longas
passariam do limite de recursão do Python (1000 chamadas).

Complexidade (V = pontos, E = tubulações, inclusive inativas):
    Tempo O(V + E): cada ponto é empilhado e desempilhado uma vez e cada
    tubulação é vista duas vezes, uma por extremo. Ordenar o resultado soma
    O(P log P), sendo P o número de pontes (P <= V - 1).
    Espaço O(V + E): descoberta e low têm um valor por ponto, e as listas de
    vizinhos guardadas na pilha somam no máximo 2E itens.

Premissas:
    - Só tubulações ativas (o filtro é feito por rede.vizinhos_ativos).
    - A rede recebida não é alterada.
    - Grafo não direcionado, sem laços nem tubulações duplicadas.
    - A rede pode ser desconexa: todas as componentes são analisadas.

Uso no projeto: a interface (app.py) destaca as pontes no desenho, e a
simulação de falhas (servicos/simulacao.py) as recalcula após cada falha,
porque uma falha pode criar pontes novas (sem D-F, E-F vira ponte).
"""


def encontrar_pontes(rede):
    """Lista as tubulações ativas que são pontes na rede.

    Args:
        rede (Rede): rede a analisar. Não é alterada.

    Returns:
        list[str]: IDs das pontes na ordem de sorted() (alfabética). Com IDs
        sem zeros à esquerda, como na base R-9, "T10" vem antes de "T2".
        Lista vazia se não houver pontes.

    Raises:
        Nenhuma exceção própria.

    Complexidade:
        Tempo O(V + E + P log P), espaço O(V + E).

    Exemplo:
        Na rede de exemplo (testes/auxiliares.criar_rede_exemplo)::

            encontrar_pontes(rede)   # ['T01', 'T10'] (R-A e F-G)
            copia = rede.copiar()
            copia.alterar_estado("T08", False)   # desativa D-F
            encontrar_pontes(copia)  # ['T01', 'T09', 'T10'] (E-F vira ponte)
    """
    # descoberta[p]: ordem em que p foi visitado (0, 1, 2, ...). Também serve
    # de conjunto de visitados e é compartilhado entre as componentes.
    descoberta = {}
    pontes = []

    # Uma busca só alcança a componente onde começou. Reiniciar em cada ponto
    # ainda não visitado cobre redes desconexas (comuns depois de falhas).
    for ponto in rede.vertices:
        if ponto not in descoberta:
            pontes.extend(_pontes_da_componente(rede, ponto, descoberta))

    # A ordem em que o Tarjan acha as pontes depende do cadastro; ordenar
    # deixa o resultado previsível.
    return sorted(pontes)


def _pontes_da_componente(rede, raiz, descoberta):
    """Roda o Tarjan iterativo na componente de raiz e devolve suas pontes.

    Args:
        rede (Rede): rede analisada. Não é alterada.
        raiz (str): ponto inicial, ainda fora de descoberta.
        descoberta (dict[str, int]): tempos de descoberta já atribuídos. É
            alterado no lugar: recebe os pontos desta componente.

    Returns:
        list[str]: IDs das pontes da componente, na ordem em que foram
        achadas (sem ordenar).

    Raises:
        Nenhuma exceção própria.

    Complexidade:
        Tempo e espaço O(Vc + Ec), só da componente de raiz.

    Exemplo:
        Na rede de exemplo, com descoberta = {}::

            _pontes_da_componente(rede, "R", descoberta)  # ['T10', 'T01']
    """
    # low[p]: menor tempo de descoberta que p e os pontos abaixo dele na
    # árvore da busca alcançam com no máximo uma tubulação de retorno.
    low = {}
    pontes = []

    # A pilha substitui a recursão. Cada item guarda o que uma chamada
    # recursiva guardaria: (ponto, ID da tubulação vinda do pai, iterador de
    # vizinhos). O iterador lembra até onde os vizinhos já foram examinados,
    # e o item logo abaixo na pilha é sempre o pai. Cada volta do while dá
    # um passo: examina o próximo vizinho do topo (empilhar um vizinho novo
    # = chamada recursiva) ou, se acabaram, desempilha o topo (= return).
    #
    # len(descoberta) é o próximo tempo livre, inclusive entre componentes.
    tempo = len(descoberta)
    descoberta[raiz] = tempo
    low[raiz] = tempo
    # A raiz não tem pai; None nunca é ID de tubulação.
    pilha = [(raiz, None, iter(rede.vizinhos_ativos(raiz)))]

    while pilha:
        ponto, tubulacao_do_pai, vizinhos = pilha[-1]
        proximo = next(vizinhos, None)

        if proximo is None:
            # Retorno: todos os vizinhos de ponto foram vistos, então
            # low[ponto] está pronto e é repassado ao pai.
            pilha.pop()
            if pilha:
                pai = pilha[-1][0]
                low[pai] = min(low[pai], low[ponto])

                # Ponte: ponto e tudo abaixo dele não conseguem voltar ao pai
                # nem a antes dele por outro caminho, então pai-ponto é a
                # única ligação. Se low[ponto] == descoberta[pai], há outro
                # caminho até o pai (um ciclo) e não é ponte. Só tubulações
                # da árvore são testadas: uma de retorno sempre fecha ciclo.
                if low[ponto] > descoberta[pai]:
                    pontes.append(tubulacao_do_pai)
            continue

        vizinho, _distancia = proximo
        id_tubulacao = rede.adjacencia[ponto][vizinho]

        # Ignora a volta ao pai pelo ID da tubulação, não pelo ponto: com duas
        # tubulações paralelas entre os mesmos pontos, a segunda é um caminho
        # alternativo real e não pode ser descartada. A Rede hoje proíbe
        # paralelas, mas a regra pelo ID continua certa se isso mudar.
        if id_tubulacao == tubulacao_do_pai:
            continue

        if vizinho in descoberta:
            # Tubulação de retorno (ponto já visitado): pode baixar o low.
            low[ponto] = min(low[ponto], descoberta[vizinho])
        else:
            # Tubulação da árvore: ponto novo, empilhado como uma chamada.
            tempo = len(descoberta)
            descoberta[vizinho] = tempo
            low[vizinho] = tempo
            pilha.append(
                (vizinho, id_tubulacao, iter(rede.vizinhos_ativos(vizinho)))
            )

    return pontes
