def encontrar_pontes(rede):
    """Lista as tubulacoes ativas que sao pontes (arestas críticas).

    Uma ponte e uma tubulacao cuja remocao aumenta o numero de componentes.

    Argumentos:
        rede (Rede): rede a analisar. Nao e alterada.

    Retorna:
        list[str]: IDs das tubulacoes pontes, ordenados alfabeticamente.
    """
    descoberta = {}
    low = {}
    pontes = []
    tempo = [0]  # contador mutavel para atribuir tempos de descoberta

    def dfs(ponto, pai_tubulacao):
        """Visita um no e seus vizinhos em profundidade."""
        descoberta[ponto] = tempo[0]
        low[ponto] = tempo[0]
        tempo[0] += 1

        for vizinho, _dist in rede.vizinhos_ativos(ponto):
            id_tubo = rede.adjacencia[ponto][vizinho]

            # Ignora a tubulacao usada para chegar neste no (volta ao pai)
            if id_tubo == pai_tubulacao:
                continue

            if vizinho not in descoberta:
                dfs(vizinho, id_tubo)
                low[ponto] = min(low[ponto], low[vizinho])

                # Se o vizinho nao consegue voltar ao pai nem a antes dele,
                # a tubulacao ponto-vizinho e uma ponte.
                if low[vizinho] > descoberta[ponto]:
                    pontes.append(id_tubo)
            else:
                # Tubulacao de retorno: atualiza o low com o tempo do vizinho
                low[ponto] = min(low[ponto], descoberta[vizinho])

    # Percorre todas as componentes (rede pode ser desconexa)
    for ponto in rede.vertices:
        if ponto not in descoberta:
            dfs(ponto, None)

    return sorted(pontes)
