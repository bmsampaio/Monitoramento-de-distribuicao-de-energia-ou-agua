"""Interface Streamlit do monitoramento da rede de distribuicao de agua (pessoa 4).

Usa os modulos reais do grupo: Rede (modelos/), BFS, Dijkstra e pontes
(algoritmos/) por meio de servicos/simulacao.py.

Rodar com:  python -m streamlit run app.py
"""
import re
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from exemplos.rede_exemplo import POSICOES as POSICOES_EXEMPLO
from exemplos.rede_exemplo import criar_rede_exemplo
from servicos.leitura_csv import carregar_rede
from servicos.simulacao import simular_falhas
from visualizacao import (ALTURA_EXTRA, calcular_layout, desenhar_rede,
                          figura_para_svg, html_com_zoom)

PASTA_DADOS = Path(__file__).resolve().parent / "dados"
ALTURA_DESENHO = 560  # pixels de cada desenho na tela


# ---------- Carregamento da rede ----------
@st.cache_resource
def obter_rede(nome):
    """Carrega a rede e o layout uma vez so (a rede original nunca e alterada)."""
    if nome == "Exemplo do plano (8 pontos)":
        return criar_rede_exemplo(), POSICOES_EXEMPLO
    rede = carregar_rede(PASTA_DADOS / "nos.csv", PASTA_DADOS / "tubulacoes.csv")
    return rede, calcular_layout(rede)


def ordenar_ids(ids):
    """Ordena IDs de forma natural: R primeiro, depois 1, 2, ..., 10 (e T1, T2, ..., T10)."""
    def chave(i):
        partes = re.split(r"(\d+)", i)
        return (i != "R", [int(p) if p.isdigit() else p for p in partes])
    return sorted(ids, key=chave)


def rotulo_tubulacao(rede, id_):
    t = rede.tubulacoes[id_]
    return f"{id_}: {t.origem}–{t.destino} ({t.distancia:g} km)"


def mostrar_html(pagina, altura):
    """Exibe uma pagina HTML com JavaScript (o desenho com zoom).

    st.iframe substitui st.components.v1.html nas versoes novas do Streamlit;
    o components.html fica so para versoes antigas, que nao tem st.iframe.
    """
    if hasattr(st, "iframe"):
        st.iframe(pagina, height=altura)
    else:
        import streamlit.components.v1 as components
        components.html(pagina, height=altura)


def descrever_tubulacoes(rede, ids):
    return ", ".join(f"{i} ({rede.tubulacoes[i].origem}–{rede.tubulacoes[i].destino})" for i in ids) or "nenhuma"


# ---------- Estado das falhas ----------
# "falhas" guarda as tubulacoes aplicadas; "selecao_falhas" e o valor do
# multiselect. Limpar o multiselect so e permitido antes de ele ser desenhado,
# por isso os botoes usam callbacks (on_click rodam antes do script).
def aplicar_falhas():
    st.session_state.falhas = list(st.session_state.selecao_falhas)


def limpar_falhas():
    st.session_state.falhas = []
    st.session_state.selecao_falhas = []


# ---------- Tela ----------
st.set_page_config(page_title="Rede de água", layout="wide")
st.title("Monitoramento de distribuição de água")
st.caption("Compara a rede antes e depois da interrupção de uma ou mais tubulações. "
           "Analisa conexões e distâncias; não calcula pressão nem vazão.")

with st.sidebar:
    st.header("Controles")
    nome_rede = st.selectbox("Rede", ["R-9 (62 pontos)", "Exemplo do plano (8 pontos)"])
    try:
        rede, posicoes = obter_rede(nome_rede)
    except (OSError, ValueError) as erro:
        st.error(f"Não foi possível carregar a rede: {erro}")
        st.stop()
    if st.session_state.get("rede_atual") != nome_rede:
        st.session_state.rede_atual = nome_rede
        limpar_falhas()  # trocar de rede limpa as falhas e a selecao

    pontos = ordenar_ids(rede.vertices)
    origem = st.selectbox("Origem", pontos, index=0)
    destino = st.selectbox("Destino", pontos, index=len(pontos) - 1)
    tubos = ordenar_ids(rede.tubulacoes)
    st.multiselect("Tubulações a interromper", tubos, key="selecao_falhas",
                   format_func=lambda i: rotulo_tubulacao(rede, i),
                   placeholder="Escolha uma ou mais")
    st.button("Simular falhas", type="primary", use_container_width=True,
              on_click=aplicar_falhas, disabled=not st.session_state.selecao_falhas)
    st.button("Restaurar rede", use_container_width=True, on_click=limpar_falhas)
    if st.session_state.selecao_falhas != st.session_state.get("falhas", []):
        st.caption("A seleção mudou. Clique em **Simular falhas** para aplicar.")
    rotulos = st.checkbox("Mostrar IDs dos pontos", value=True)

falhas = st.session_state.get("falhas", [])

try:
    r = simular_falhas(rede, origem, destino, falhas)
except ValueError as erro:
    st.error(f"Não foi possível simular: {erro}")
    st.stop()

if falhas:
    titulo_falhas = ("Tubulação interrompida" if len(falhas) == 1
                     else f"{len(falhas)} tubulações interrompidas")
    st.error(f"{titulo_falhas}: " + "; ".join(rotulo_tubulacao(rede, i) for i in falhas))
else:
    st.success("Rede original, sem falhas. Escolha uma ou mais tubulações e clique em "
               "**Simular falhas**.")

# --- Comparação antes/depois ---
antes_d, depois_d = r["distancia_antes"], r["distancia_depois"]
c1, c2, c3 = st.columns(3)
with c1:
    if antes_d is None:
        st.metric("Distância antes", "sem caminho")
    else:
        st.metric("Distância antes", f"{antes_d:.2f} km")
with c2:
    if depois_d is None:
        st.metric("Distância depois", "sem caminho")
    elif antes_d is None or not falhas:
        st.metric("Distância depois", f"{depois_d:.2f} km")
    else:
        st.metric("Distância depois", f"{depois_d:.2f} km", delta=f"{depois_d - antes_d:+.2f} km",
                  delta_color="inverse")
with c3:
    st.metric("Pontos inacessíveis por causa das falhas", len(r["inacessiveis_apos_falha"]))

if r["caminho_antes"] is None:
    st.warning(f"Sem caminho entre {origem} e {destino} na rede original.")
elif falhas and r["caminho_depois"] is None:
    st.warning(f"Sem caminho entre {origem} e {destino} depois das falhas: "
               f"{destino} ficou isolado de {origem}.")

# --- Desenhos lado a lado, com zoom ---
if not falhas:
    titulo_depois = "Sem falha (igual ao antes)"
elif len(falhas) == 1:
    titulo_depois = "Depois da falha"
else:
    titulo_depois = f"Depois das {len(falhas)} falhas"

# Titulos e legenda ficam no HTML, fora do desenho, para nao sumirem no zoom.
figuras = [
    desenhar_rede(rede, posicoes, origem, destino, caminho=r["caminho_antes"],
                  pontes=r["pontes_antes"], rotulos=rotulos, legenda=False),
    desenhar_rede(rede, posicoes, origem, destino, caminho=r["caminho_depois"],
                  pontes=r["pontes_depois"] or [], falhas=falhas,
                  inacessiveis=r["inacessiveis_apos_falha"], rotulos=rotulos, legenda=False),
]
svgs = [figura_para_svg(fig) for fig in figuras]
for fig in figuras:
    plt.close(fig)
mostrar_html(
    html_com_zoom(svgs, ["Antes das falhas", titulo_depois], ALTURA_DESENHO, chave=nome_rede),
    ALTURA_DESENHO + ALTURA_EXTRA,
)

# --- Detalhes ---
st.subheader("Detalhes")
d1, d2 = st.columns(2)
with d1:
    st.markdown("**Caminho antes:** " + (" → ".join(r["caminho_antes"]) if r["caminho_antes"] else "sem caminho"))
    st.markdown("**Pontes antes:** " + descrever_tubulacoes(rede, r["pontes_antes"]))
with d2:
    st.markdown("**Caminho depois:** " + (" → ".join(r["caminho_depois"]) if r["caminho_depois"] else "sem caminho"))
    st.markdown("**Pontes depois:** " + descrever_tubulacoes(rede, r["pontes_depois"] or []))
    if falhas:
        st.markdown("**Pontos inacessíveis:** "
                    + (", ".join(ordenar_ids(r["inacessiveis_apos_falha"])) or "nenhum"))
        st.markdown("**Novas pontes:** " + descrever_tubulacoes(rede, r["novas_pontes"]))
