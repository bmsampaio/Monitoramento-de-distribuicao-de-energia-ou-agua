"""Desenho da rede com Matplotlib (pessoa 4).

Nao usa NetworkX: o layout e calculado aqui, com um algoritmo de forcas
simples (tipo Fruchterman-Reingold) escrito com numpy. A base R-9 nao tem
coordenadas, entao as posicoes sao so para o desenho; as distancias em km
dos tubos ficam nos dados, nao no comprimento das linhas.

Na interface, as figuras sao exibidas como SVG com zoom (html_com_zoom):
aproximar afasta os pontos sem aumentar circulos, textos e linhas.
"""
import io
import json
import math
import re
from html import escape

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


def _distancia_ao_segmento(p, a, b):
    """Menor distancia do ponto p ao segmento a-b (tuplas x, y)."""
    ab = (b[0] - a[0], b[1] - a[1])
    tamanho2 = ab[0] ** 2 + ab[1] ** 2
    t = 0.0 if tamanho2 == 0 else max(0.0, min(1.0, (
        (p[0] - a[0]) * ab[0] + (p[1] - a[1]) * ab[1]) / tamanho2))
    return math.hypot(p[0] - (a[0] + t * ab[0]), p[1] - (a[1] + t * ab[1]))


def _tracado_tubulacao(origem, destino, posicoes, folga=0.03):
    """Pontos (x, y) do desenho de uma tubulacao.

    Se a reta passa por cima de outro ponto (ex.: 5-27 atras do 34), o tubo
    vira uma curva que contorna o ponto, para nao parecer que passa por ele.

    Returns:
        tuple[list[float], list[float]]: listas x e y (2 pontos se for reta).
    """
    a, b = posicoes[origem], posicoes[destino]
    outros = [p for id_, p in posicoes.items() if id_ not in (origem, destino)]
    if all(_distancia_ao_segmento(p, a, b) >= folga for p in outros):
        return [a[0], b[0]], [a[1], b[1]]
    comprimento = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    normal = (-(b[1] - a[1]) / comprimento, (b[0] - a[0]) / comprimento)
    meio = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    for desvio in (0.09, -0.09, 0.16, -0.16, 0.24, -0.24):
        c = (meio[0] + normal[0] * desvio, meio[1] + normal[1] * desvio)
        ts = [i / 24 for i in range(25)]
        curva = [((1 - t) ** 2 * a[0] + 2 * t * (1 - t) * c[0] + t * t * b[0],
                  (1 - t) ** 2 * a[1] + 2 * t * (1 - t) * c[1] + t * t * b[1]) for t in ts]
        if all(min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in curva) >= folga
               for p in outros):
            return [q[0] for q in curva], [q[1] for q in curva]
    return [a[0], b[0]], [a[1], b[1]]


def desenhar_rede(rede, posicoes, origem, destino, caminho=None, pontes=(),
                  falhas=(), inacessiveis=(), titulo="", rotulos=True,
                  tamanho=(7.5, 6), legenda=True):
    """Desenha a rede destacando caminho, pontes, falhas e pontos inacessiveis.

    Cada elemento recebe um gid ("aresta-T1", "no-R", "rotulo-R", "km-T1"),
    que vira o id do grupo no SVG e e usado pelo zoom de html_com_zoom.

    Args:
        rede (Rede): rede a desenhar (so le; nao altera).
        posicoes (dict): resultado de calcular_layout (ou posicoes fixas).
        origem (str): ID da origem (destacada).
        destino (str): ID do destino (destacado).
        caminho (list[str] | None): sequencia de pontos do menor caminho.
        pontes (iterable[str]): IDs das tubulacoes que sao pontes.
        falhas (iterable[str]): IDs das tubulacoes interrompidas.
        inacessiveis (iterable[str]): IDs dos pontos que perderam o acesso.
        titulo (str): titulo do desenho.
        rotulos (bool): se True, escreve o ID dentro de cada ponto.
        tamanho (tuple): tamanho da figura em polegadas.
        legenda (bool): se False, nao desenha a legenda (html_com_zoom tem a sua).

    Returns:
        matplotlib.figure.Figure: figura pronta para st.pyplot ou figura_para_svg.
    """
    fig, ax = plt.subplots(figsize=tamanho)
    pontes = set(pontes)
    falhas = set(falhas)
    inacessiveis = set(inacessiveis)
    arestas_caminho = set()
    if caminho:
        arestas_caminho = {frozenset(par) for par in zip(caminho, caminho[1:])}

    # Em caminhos longos os rotulos de km se sobrepoem; os valores ficam nos detalhes.
    rotular_km = len(arestas_caminho) <= 6
    for t in rede.tubulacoes.values():
        x, y = _tracado_tubulacao(t.origem, t.destino, posicoes)
        meio = len(x) // 2
        mx = sum(x) / 2 if len(x) == 2 else x[meio]
        my = sum(y) / 2 if len(y) == 2 else y[meio]
        par = frozenset((t.origem, t.destino))
        falhou = t.identificador in falhas
        if falhou:
            estilo = dict(color=COR_FALHA, linestyle="--", linewidth=2.5, zorder=2)
        elif par in arestas_caminho:
            estilo = dict(color=COR_CAMINHO, linestyle="-", linewidth=4, zorder=2)
        elif t.identificador in pontes:
            estilo = dict(color=COR_PONTE, linestyle="-", linewidth=3, zorder=1)
        else:
            estilo = dict(color=COR_NORMAL, linestyle="-", linewidth=1.2, zorder=1)
        ax.plot(x, y, gid=f"aresta-{t.identificador}", **estilo)
        if falhou or (par in arestas_caminho and rotular_km):
            ax.text(mx, my + (0.03 if falhou else 0), f"{t.distancia:g} km", fontsize=7,
                    ha="center", va="center", zorder=4, gid=f"km-{t.identificador}",
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
        ax.scatter(x, y, s=260, color=cor, edgecolor=borda, linewidths=largura, zorder=3,
                   gid=f"no-{id_}")
        if rotulos:
            ax.text(x, y, id_, ha="center", va="center", fontsize=6.5, zorder=5,
                    color="white" if id_ == origem else "black", gid=f"rotulo-{id_}")

    if legenda:
        itens = [
            Line2D([0], [0], color=COR_CAMINHO, lw=4, label="Menor caminho"),
            Line2D([0], [0], color=COR_PONTE, lw=3, label="Ponte (tubulação crítica)"),
            Line2D([0], [0], color=COR_FALHA, lw=2.5, ls="--", label="Tubulação interrompida"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COR_NO_INACESSIVEL,
                   markeredgecolor="#555555", markersize=10, label="Ponto inacessível"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor=COR_ORIGEM,
                   markeredgecolor="black", markersize=10, label="Origem"),
        ]
        ax.legend(handles=itens, loc="upper center", bbox_to_anchor=(0.5, -0.01),
                  ncol=3, fontsize=7.5, frameon=False)
    ax.set_title(titulo, fontsize=11)
    ax.set_axis_off()
    ax.margins(0.06)
    fig.tight_layout()
    return fig


# ---------- Exibicao com zoom ----------
# Altura, em pixels, que html_com_zoom usa alem dos desenhos (titulos,
# legenda e controles). A altura do componente e altura + ALTURA_EXTRA.
ALTURA_EXTRA = 120


def figura_para_svg(fig):
    """Converte uma figura do Matplotlib em um elemento <svg> para embutir em HTML.

    Args:
        fig (matplotlib.figure.Figure): figura de desenhar_rede.

    Returns:
        str: o <svg>, sem o cabecalho XML e sem largura/altura fixas (o
        tamanho passa a vir do CSS da pagina).
    """
    buffer = io.StringIO()
    fig.savefig(buffer, format="svg")
    svg = buffer.getvalue()
    svg = svg[svg.index("<svg"):]
    return re.sub(r'\s(width|height)="[^"]*pt"', "", svg, count=2)


def html_com_zoom(svgs, titulos, altura=520, chave="rede"):
    """Monta uma pagina com os desenhos lado a lado, zoom e legenda.

    Rolar o mouse aproxima ou afasta em volta do cursor, arrastar move e
    dois cliques voltam a rede inteira. O zoom afasta os pontos bem mais do
    que aumenta circulos, textos e linhas (a 5x, as distancias crescem 5x e
    os circulos ~1,5x), para separar pontos proximos. O zoom vale para todos
    os desenhos ao mesmo tempo, para comparar a mesma regiao antes e depois,
    e e lembrado entre simulacoes.

    Args:
        svgs (list[str]): desenhos de figura_para_svg, do mesmo tamanho.
        titulos (list[str]): titulo de cada desenho.
        altura (int): altura de cada desenho, em pixels.
        chave (str): identifica a rede; o zoom lembrado e por chave.

    Returns:
        str: pagina HTML para st.components.v1.html, com altura
        altura + ALTURA_EXTRA.
    """
    paineis = "".join(
        f'<figure class="painel"><figcaption>{escape(titulo)}</figcaption>'
        f'<div class="desenho">{svg}</div></figure>'
        for svg, titulo in zip(svgs, titulos)
    )
    legenda = "".join([
        _item_linha(f"4px solid {COR_CAMINHO}", "Menor caminho"),
        _item_linha(f"3px solid {COR_PONTE}", "Ponte (tubulação crítica)"),
        _item_linha(f"3px dashed {COR_FALHA}", "Tubulação interrompida"),
        _item_ponto(COR_NO_INACESSIVEL, "#555555", "Ponto inacessível"),
        _item_ponto(COR_ORIGEM, "black", "Origem"),
    ])
    script = _SCRIPT_ZOOM.replace("__CHAVE__", json.dumps("zoom-rede:" + chave))
    # Os SVGs entram por ultimo, para o texto deles nao passar pelos replace.
    return (_PAGINA_ZOOM
            .replace("__ALTURA__", str(int(altura)))
            .replace("__COLUNAS__", str(len(svgs)))
            .replace("__LEGENDA__", legenda)
            .replace("__SCRIPT__", script)
            .replace("__PAINEIS__", paineis))


def _item_linha(borda, texto):
    return (f'<span class="item"><i class="linha" style="border-top: {borda}"></i>'
            f'{escape(texto)}</span>')


def _item_ponto(cor, borda, texto):
    return (f'<span class="item"><i class="ponto" style="background: {cor}; '
            f'border-color: {borda}"></i>{escape(texto)}</span>')


_PAGINA_ZOOM = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><style>
body { margin: 0; color: #262730;
       font-family: "Source Sans Pro", "Source Sans 3", system-ui, sans-serif; }
.paineis { display: grid; grid-template-columns: repeat(__COLUNAS__, minmax(0, 1fr)); gap: 12px; }
.painel { margin: 0; background: #fff; border: 1px solid #e3e3e8; border-radius: 8px;
          overflow: hidden; }
.painel figcaption { height: 30px; line-height: 30px; text-align: center;
                     font-size: 15px; font-weight: 600; }
.desenho { height: __ALTURA__px; }
.desenho svg { display: block; width: 100%; height: 100%; cursor: grab;
               touch-action: none; user-select: none; }
.desenho svg.arrastando { cursor: grabbing; }
.barra { margin-top: 10px; padding: 6px 12px; background: #fff; border: 1px solid #e3e3e8;
         border-radius: 8px; display: flex; flex-wrap: wrap; align-items: center;
         gap: 6px 18px; font-size: 13px; }
.item { display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.linha { display: inline-block; width: 26px; }
.ponto { display: inline-block; width: 11px; height: 11px; border: 1px solid;
         border-radius: 50%; }
.dica { color: #5f6170; }
.controles { margin-left: auto; display: inline-flex; align-items: center; gap: 6px; }
.controles button { min-width: 30px; height: 26px; padding: 0 8px; font: inherit;
                    color: #262730; background: #fff; border: 1px solid #c9c9d1;
                    border-radius: 6px; cursor: pointer; }
.controles button:hover { border-color: #2166ac; color: #2166ac; }
#nivel { min-width: 38px; text-align: right; font-variant-numeric: tabular-nums; }
</style></head><body>
<div class="paineis">__PAINEIS__</div>
<div class="barra">__LEGENDA__
<span class="dica">Role para aproximar, arraste para mover, 2 cliques para voltar.</span>
<span class="controles">
<button id="afastar" title="Afastar">&minus;</button>
<button id="aproximar" title="Aproximar">+</button>
<button id="ajustar" title="Mostrar a rede inteira">Ajustar</button>
<span id="nivel">1x</span>
</span>
</div>
<script>__SCRIPT__</script>
</body></html>"""


_SCRIPT_ZOOM = """
(function () {
  var svgs = Array.prototype.slice.call(document.querySelectorAll('.desenho svg'));
  if (!svgs.length) return;
  var ZOOM_MAXIMO = 25;
  // Com zoom Z, as distancias crescem Z vezes e circulos, textos e linhas
  // crescem Z^(1 - EXPOENTE) vezes: a 5x, ficam ~1,5x maiores. Assim os
  // pontos se separam e os numeros ficam mais legiveis.
  var EXPOENTE = 0.75;
  var CHAVE = __CHAVE__;
  var base = svgs[0].viewBox.baseVal;
  var inicial = {x: base.x, y: base.y, w: base.width, h: base.height};
  var vista = {x: inicial.x, y: inicial.y, w: inicial.w, h: inicial.h};
  var escalaAplicada = 1;
  var nivel = document.getElementById('nivel');

  // Pontos, IDs e rotulos de km quase nao crescem com o zoom: a cada zoom,
  // sao reduzidos em volta de uma ancora. A ancora do ID e o
  // centro do seu ponto, e a do rotulo de km e o meio da sua tubulacao; se
  // fosse o centro do proprio texto, a pequena distancia entre os dois
  // cresceria com o zoom e o texto sairia do lugar.
  var fixos = [];
  // Espessura e tracejado das tubulacoes seguem a mesma regra.
  var arestas = [];
  function centro(el) {
    var b = el.getBBox();
    return {x: b.x + b.width / 2, y: b.y + b.height / 2};
  }
  svgs.forEach(function (svg) {
    var ancoras = {};
    svg.querySelectorAll('[id^="no-"], [id^="aresta-"]').forEach(function (el) {
      ancoras[el.id] = el;
    });
    svg.querySelectorAll('[id^="no-"], [id^="rotulo-"], [id^="km-"]').forEach(function (el) {
      var ancora = el;
      if (el.id.indexOf('rotulo-') === 0) ancora = ancoras['no-' + el.id.slice(7)] || el;
      if (el.id.indexOf('km-') === 0) ancora = ancoras['aresta-' + el.id.slice(3)] || el;
      var c = centro(ancora);
      fixos.push({el: el, cx: c.x, cy: c.y});
    });
    svg.querySelectorAll('[id^="aresta-"] path').forEach(function (p) {
      var traco = (p.style.strokeDasharray || '').split(/[\\s,]+/).filter(Boolean).map(parseFloat);
      arestas.push({el: p, largura: parseFloat(p.style.strokeWidth) || 1, traco: traco});
    });
  });

  function limitar() {
    vista.w = Math.min(inicial.w, Math.max(inicial.w / ZOOM_MAXIMO, vista.w));
    vista.h = vista.w * inicial.h / inicial.w;
    vista.x = Math.min(inicial.x + inicial.w - vista.w, Math.max(inicial.x, vista.x));
    vista.y = Math.min(inicial.y + inicial.h - vista.h, Math.max(inicial.y, vista.y));
  }

  function aplicar() {
    limitar();
    var caixa = vista.x + ' ' + vista.y + ' ' + vista.w + ' ' + vista.h;
    svgs.forEach(function (svg) { svg.setAttribute('viewBox', caixa); });
    var k = vista.w / inicial.w;  // 1 sem zoom; 1/Z com zoom Z
    if (k !== escalaAplicada) {
      escalaAplicada = k;
      var s = Math.pow(k, EXPOENTE);
      fixos.forEach(function (f) {
        if (k === 1) { f.el.removeAttribute('transform'); return; }
        f.el.setAttribute('transform', 'translate(' + f.cx + ' ' + f.cy + ') scale(' + s +
                          ') translate(' + (-f.cx) + ' ' + (-f.cy) + ')');
      });
      arestas.forEach(function (a) {
        a.el.style.strokeWidth = a.largura * s;
        if (a.traco.length) {
          a.el.style.strokeDasharray = a.traco.map(function (v) { return v * s; }).join(' ');
        }
      });
    }
    nivel.textContent = (1 / k).toLocaleString('pt-BR', {maximumFractionDigits: 1}) + 'x';
    try { sessionStorage.setItem(CHAVE, JSON.stringify(vista)); } catch (e) {}
  }

  function pontoNoDesenho(svg, x, y) {
    var p = svg.createSVGPoint();
    p.x = x;
    p.y = y;
    return p.matrixTransform(svg.getScreenCTM().inverse());
  }

  // fator > 1 aproxima; o ponto sob o cursor fica parado na tela.
  function zoom(svg, fator, x, y) {
    var p = pontoNoDesenho(svg, x, y);
    var largura = Math.min(inicial.w, Math.max(inicial.w / ZOOM_MAXIMO, vista.w / fator));
    var r = largura / vista.w;
    vista = {x: p.x - (p.x - vista.x) * r, y: p.y - (p.y - vista.y) * r,
             w: largura, h: vista.h * r};
    aplicar();
  }

  function noCentro(fator) {
    var r = svgs[0].getBoundingClientRect();
    zoom(svgs[0], fator, r.left + r.width / 2, r.top + r.height / 2);
  }

  function ajustar() {
    vista = {x: inicial.x, y: inicial.y, w: inicial.w, h: inicial.h};
    aplicar();
  }

  svgs.forEach(function (svg) {
    svg.addEventListener('wheel', function (e) {
      e.preventDefault();
      var passo = e.deltaMode === 1 ? e.deltaY * 40 : e.deltaY;
      zoom(svg, Math.exp(-passo * 0.002), e.clientX, e.clientY);
    }, {passive: false});

    var arrasto = null;
    svg.addEventListener('pointerdown', function (e) {
      if (e.button !== 0) return;
      var m = svg.getScreenCTM();
      arrasto = {x: e.clientX, y: e.clientY, vx: vista.x, vy: vista.y, sx: m.a, sy: m.d};
      svg.setPointerCapture(e.pointerId);
      svg.classList.add('arrastando');
    });
    svg.addEventListener('pointermove', function (e) {
      if (!arrasto) return;
      vista.x = arrasto.vx - (e.clientX - arrasto.x) / arrasto.sx;
      vista.y = arrasto.vy - (e.clientY - arrasto.y) / arrasto.sy;
      aplicar();
    });
    function soltar() { arrasto = null; svg.classList.remove('arrastando'); }
    svg.addEventListener('pointerup', soltar);
    svg.addEventListener('pointercancel', soltar);
    svg.addEventListener('dblclick', ajustar);
  });

  document.getElementById('aproximar').onclick = function () { noCentro(1.5); };
  document.getElementById('afastar').onclick = function () { noCentro(1 / 1.5); };
  document.getElementById('ajustar').onclick = ajustar;

  // Volta ao zoom da simulacao anterior (a pagina e recriada a cada clique).
  try {
    var salvo = JSON.parse(sessionStorage.getItem(CHAVE));
    if (salvo && salvo.w > 0) vista = salvo;
  } catch (e) {}
  aplicar();
})();
"""
