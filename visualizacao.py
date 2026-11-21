"""Desenho da rede com Matplotlib (pessoa 4).

Nao usa NetworkX: o layout e calculado aqui, com um algoritmo de forcas
simples (tipo Fruchterman-Reingold) escrito com numpy. A base R-9 nao tem
coordenadas, entao as posicoes sao so para o desenho; as distancias em km
dos tubos ficam nos dados, nao no comprimento das linhas.
"""
import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

COR_CAMINHO = "#1a9850"
COR_PONTE = "#f28e2b"
COR_FALHA = "#d62728"
COR_NORMAL = "#9aa0a6"
COR_NO = "#8ecae6"
COR_NO_INACESSIVEL = "#d9d9d9"
COR_ORIGEM = "#2166ac"


def calcular_layout(rede, semente=7, iteracoes=400):
    """Calcula posicoes (x, y) para cada ponto, sem NetworkX.

    Args:
        rede (Rede): rede cujos pontos serao posicionados.
        semente (int): semente aleatoria, para o desenho nao mudar a cada clique.
        iteracoes (int): numero de passos do algoritmo de forcas.

    Returns:
        dict[str, tuple[float, float]]: ID do ponto -> (x, y) entre 0 e 1.
    """
    ids = list(rede.vertices)
    n = len(ids)
    if n == 0:
        return {}
    if n == 1:
        return {ids[0]: (0.5, 0.5)}
    indice = {id_: i for i, id_ in enumerate(ids)}
    arestas = np.array(
        [(indice[t.origem], indice[t.destino]) for t in rede.tubulacoes.values()],
        dtype=int,
    ).reshape(-1, 2)

    gerador = np.random.default_rng(semente)
    pos = gerador.random((n, 2))
    k = 1.6 * math.sqrt(1.0 / n)
    temperatura = 0.1
    for _ in range(iteracoes):
        delta = pos[:, None, :] - pos[None, :, :]
        dist = np.linalg.norm(delta, axis=-1)
        np.fill_diagonal(dist, 1.0)
        dist = np.maximum(dist, 1e-3)
        repulsao = (delta / dist[..., None]) * (k * k / dist)[..., None]
        deslocamento = repulsao.sum(axis=1)
        for a, b in arestas:
            d = pos[a] - pos[b]
            comprimento = max(float(np.linalg.norm(d)), 1e-3)
            forca = d / comprimento * (comprimento * comprimento / k)
            deslocamento[a] -= forca
            deslocamento[b] += forca
        tamanho = np.maximum(np.linalg.norm(deslocamento, axis=1), 1e-3)
        pos += deslocamento / tamanho[:, None] * np.minimum(tamanho, temperatura)[:, None]
        temperatura = max(temperatura * 0.985, 0.002)

    pos -= pos.min(axis=0)
    amplitude = pos.max(axis=0)
    amplitude[amplitude == 0] = 1
    pos /= amplitude

    # Afasta pontos que ficaram colados, para os circulos nao se sobreporem.
    distancia_minima = min(0.06, 0.8 / math.sqrt(n))
    for _ in range(200):
        movido = False
        for i in range(n):
            for j in range(i + 1, n):
                d = pos[i] - pos[j]
                comprimento = float(np.linalg.norm(d))
                if comprimento < distancia_minima:
                    if comprimento < 1e-6:
                        d, comprimento = gerador.random(2) - 0.5, 1e-3
                    empurrao = d / max(comprimento, 1e-6) * (distancia_minima - comprimento) / 2
                    pos[i] += empurrao
                    pos[j] -= empurrao
                    movido = True
        if not movido:
            break
    pos -= pos.min(axis=0)
    amplitude = pos.max(axis=0)
    amplitude[amplitude == 0] = 1
    pos /= amplitude
    return {id_: (float(pos[i, 0]), float(pos[i, 1])) for id_, i in indice.items()}


def desenhar_rede(rede, posicoes, origem, destino, caminho=None, pontes=(),
                  falha_id=None, inacessiveis=(), titulo="", rotulos=True,
                  tamanho=(7.5, 6)):
    """Desenha a rede destacando caminho, pontes, falha e pontos inacessiveis.

    Args:
        rede (Rede): rede a desenhar (so le; nao altera).
        posicoes (dict): resultado de calcular_layout (ou posicoes fixas).
        origem (str): ID da origem (destacada).
        destino (str): ID do destino (destacado).
        caminho (list[str] | None): sequencia de pontos do menor caminho.
        pontes (iterable[str]): IDs das tubulacoes que sao pontes.
        falha_id (str | None): ID da tubulacao interrompida.
        inacessiveis (iterable[str]): IDs dos pontos que perderam o acesso.
        titulo (str): titulo do desenho.
        rotulos (bool): se True, escreve o ID dentro de cada ponto.
        tamanho (tuple): tamanho da figura em polegadas.

    Returns:
        matplotlib.figure.Figure: figura pronta para st.pyplot.
    """
    fig, ax = plt.subplots(figsize=tamanho)
    pontes = set(pontes)
    inacessiveis = set(inacessiveis)
    arestas_caminho = set()
    if caminho:
        arestas_caminho = {frozenset(par) for par in zip(caminho, caminho[1:])}

    # Em caminhos longos os rotulos de km se sobrepoem; os valores ficam nos detalhes.
    rotular_km = len(arestas_caminho) <= 6
    for t in rede.tubulacoes.values():
        x = [posicoes[t.origem][0], posicoes[t.destino][0]]
        y = [posicoes[t.origem][1], posicoes[t.destino][1]]
        par = frozenset((t.origem, t.destino))
        if t.identificador == falha_id:
            estilo = dict(color=COR_FALHA, linestyle="--", linewidth=2.5, zorder=2)
        elif par in arestas_caminho:
            estilo = dict(color=COR_CAMINHO, linestyle="-", linewidth=4, zorder=2)
        elif t.identificador in pontes:
            estilo = dict(color=COR_PONTE, linestyle="-", linewidth=3, zorder=1)
        else:
            estilo = dict(color=COR_NORMAL, linestyle="-", linewidth=1.2, zorder=1)
        ax.plot(x, y, **estilo)
        if t.identificador == falha_id or (par in arestas_caminho and rotular_km):
            ax.text(sum(x) / 2, sum(y) / 2 + (0.03 if t.identificador == falha_id else 0), f"{t.distancia:g} km", fontsize=7,
                    ha="center", va="center", zorder=4,
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))

    for id_, (x, y) in posicoes.items():
        if id_ in inacessiveis:
            cor = COR_NO_INACESSIVEL
        elif id_ == origem:
            cor = COR_ORIGEM
        else:
            cor = COR_NO
        borda = "black" if id_ in (origem, destino) else "#555555"
        largura = 2.2 if id_ in (origem, destino) else 0.8
        ax.scatter(x, y, s=260, color=cor, edgecolor=borda, linewidths=largura, zorder=3)
        if rotulos:
            ax.text(x, y, id_, ha="center", va="center", fontsize=6.5, zorder=5,
                    color="white" if id_ == origem else "black")

    legenda = [
        Line2D([0], [0], color=COR_CAMINHO, lw=4, label="Menor caminho"),
        Line2D([0], [0], color=COR_PONTE, lw=3, label="Ponte (tubulação crítica)"),
        Line2D([0], [0], color=COR_FALHA, lw=2.5, ls="--", label="Tubulação interrompida"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COR_NO_INACESSIVEL,
               markeredgecolor="#555555", markersize=10, label="Ponto inacessível"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=COR_ORIGEM,
               markeredgecolor="black", markersize=10, label="Origem"),
    ]
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.5, -0.01),
              ncol=3, fontsize=7.5, frameon=False)
    ax.set_title(titulo, fontsize=11)
    ax.set_axis_off()
    ax.margins(0.06)
    fig.tight_layout()
    return fig
