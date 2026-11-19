"""Interface Streamlit do monitoramento da rede de distribuicao de agua (pessoa 4).

Usa os modulos reais do grupo: Rede (modelos/), BFS, Dijkstra e pontes
(algoritmos/) por meio de servicos/simulacao.py.

Rodar com:  python -m streamlit run app.py
"""
import csv
import re
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao
from servicos.simulacao import simular_falha
from visualizacao import calcular_layout, desenhar_rede

PASTA_DADOS = Path(__file__).resolve().parent / "dados"


# ---------- Carregamento da rede ----------
def carregar_rede_csv():
    """Le dados/nos.csv e dados/tubulacoes.csv e monta a Rede.

    PROVISORIO: serve ate o servicos/leitura_csv.py (pessoa 1) ficar pronto.
    Quando ele existir, troque o corpo desta funcao pela chamada dele.
    """
    rede = Rede()
    with open(PASTA_DADOS / "nos.csv", encoding="utf-8", newline="") as arq:
        for linha in csv.DictReader(arq):
            rede.adicionar_no(No(linha["id"], linha["nome"], linha["tipo"]))
    with open(PASTA_DADOS / "tubulacoes.csv", encoding="utf-8", newline="") as arq:
        for linha in csv.DictReader(arq):
            rede.adicionar_tubulacao(Tubulacao(
                linha["id"], linha["origem"], linha["destino"],
                float(linha["distancia_km"]), linha["ativa"].strip().lower() == "true",
            ))
    return rede


POSICOES_EXEMPLO = {
    "R": (0.0, 0.5), "A": (0.18, 0.5), "B": (0.4, 0.9), "C": (0.4, 0.1),
    "D": (0.62, 0.9), "E": (0.62, 0.1), "F": (0.82, 0.5), "G": (1.0, 0.5),
}
TUBOS_EXEMPLO = [
    ("T01", "R", "A", 2), ("T02", "A", "B", 2), ("T03", "A", "C", 3),
    ("T04", "B", "D", 2), ("T05", "B", "E", 5), ("T06", "C", "D", 6),
    ("T07", "C", "E", 4), ("T08", "D", "F", 2), ("T09", "E", "F", 3),
    ("T10", "F", "G", 2),
]


def montar_rede_exemplo():
    """Rede de 8 pontos e 10 tubulacoes da pagina 6 do plano (para os testes)."""
    rede = Rede()
    for id_ in POSICOES_EXEMPLO:
        rede.adicionar_no(No(id_, f"Ponto {id_}", "reservatorio" if id_ == "R" else "ponto_demanda"))
    for id_, o, d, km in TUBOS_EXEMPLO:
        rede.adicionar_tubulacao(Tubulacao(id_, o, d, km))
    return rede


@st.cache_resource
def obter_rede(nome):
    """Carrega a rede e o layout uma vez so (a rede original nunca e alterada)."""
    if nome == "Exemplo do plano (8 pontos)":
        return montar_rede_exemplo(), POSICOES_EXEMPLO
    rede = carregar_rede_csv()
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


def descrever_tubulacoes(rede, ids):
    return ", ".join(f"{i} ({rede.tubulacoes[i].origem}–{rede.tubulacoes[i].destino})" for i in ids) or "nenhuma"


# ---------- Tela ----------
st.set_page_config(page_title="Rede de água", layout="wide")
st.title("Monitoramento de distribuição de água")
st.caption("Compara a rede antes e depois da interrupção de uma tubulação. "
           "Analisa conexões e distâncias; não calcula pressão nem vazão.")

with st.sidebar:
    st.header("Controles")
    nome_rede = st.selectbox("Rede", ["R-9 (62 pontos)", "Exemplo do plano (8 pontos)"])
    rede, posicoes = obter_rede(nome_rede)
    if st.session_state.get("rede_atual") != nome_rede:
        st.session_state.rede_atual = nome_rede
        st.session_state.falha_id = None  # trocar de rede limpa a falha

    pontos = ordenar_ids(rede.vertices)
    origem = st.selectbox("Origem", pontos, index=0)
    destino = st.selectbox("Destino", pontos, index=len(pontos) - 1)
    tubos = ordenar_ids(rede.tubulacoes)
    escolhida = st.selectbox("Tubulação a interromper", tubos,
                             format_func=lambda i: rotulo_tubulacao(rede, i))
    if st.button("Simular falha", type="primary", use_container_width=True):
        st.session_state.falha_id = escolhida
    if st.button("Restaurar rede", use_container_width=True):
        st.session_state.falha_id = None
    rotulos = st.checkbox("Mostrar IDs dos pontos", value=True)

falha_id = st.session_state.get("falha_id")

try:
    r = simular_falha(rede, origem, destino, falha_id)
except ValueError as erro:
    st.error(f"Não foi possível simular: {erro}")
    st.stop()

if falha_id:
    st.error(f"Tubulação interrompida: {rotulo_tubulacao(rede, falha_id)}")
else:
    st.success("Rede original, sem falhas. Escolha uma tubulação e clique em **Simular falha**.")

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
    elif antes_d is None or not falha_id:
        st.metric("Distância depois", f"{depois_d:.2f} km")
    else:
        st.metric("Distância depois", f"{depois_d:.2f} km", delta=f"{depois_d - antes_d:+.2f} km",
                  delta_color="inverse")
with c3:
    st.metric("Pontos inacessíveis por causa da falha", len(r["inacessiveis_apos_falha"]))

if r["caminho_antes"] is None:
    st.warning(f"Sem caminho entre {origem} e {destino} na rede original.")
elif falha_id and r["caminho_depois"] is None:
    st.warning(f"Sem caminho entre {origem} e {destino} depois da falha: "
               f"{destino} ficou isolado de {origem}.")

# --- Desenhos lado a lado ---
col_antes, col_depois = st.columns(2)
with col_antes:
    fig = desenhar_rede(rede, posicoes, origem, destino, caminho=r["caminho_antes"],
                        pontes=r["pontes_antes"], titulo="Antes da falha", rotulos=rotulos)
    st.pyplot(fig)
    plt.close(fig)
with col_depois:
    fig = desenhar_rede(rede, posicoes, origem, destino, caminho=r["caminho_depois"],
                        pontes=r["pontes_depois"] or [], falha_id=falha_id,
                        inacessiveis=r["inacessiveis_apos_falha"],
                        titulo="Depois da falha" if falha_id else "Sem falha (igual ao antes)",
                        rotulos=rotulos)
    st.pyplot(fig)
    plt.close(fig)

# --- Detalhes ---
st.subheader("Detalhes")
d1, d2 = st.columns(2)
with d1:
    st.markdown("**Caminho antes:** " + (" → ".join(r["caminho_antes"]) if r["caminho_antes"] else "sem caminho"))
    st.markdown("**Pontes antes:** " + descrever_tubulacoes(rede, r["pontes_antes"]))
with d2:
    st.markdown("**Caminho depois:** " + (" → ".join(r["caminho_depois"]) if r["caminho_depois"] else "sem caminho"))
    st.markdown("**Pontes depois:** " + descrever_tubulacoes(rede, r["pontes_depois"] or []))
    if falha_id:
        st.markdown("**Pontos inacessíveis:** " + (", ".join(r["inacessiveis_apos_falha"]) or "nenhum"))
        st.markdown("**Novas pontes:** " + descrever_tubulacoes(rede, r["novas_pontes"]))
