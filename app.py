"""Tela provisória (pessoa 4) - rede de distribuição de água.

ATENÇÃO: os resultados abaixo são FIXOS, apenas para desenvolvimento.
Depois que a pessoa 5 entregar o serviço de simulação, troque
`resultado_exemplo` pela chamada real.

Rodar com:  streamlit run app.py
"""
import streamlit as st
import matplotlib.pyplot as plt

# ---------- Dados de exemplo (página 6 do plano) ----------
# id: (nome, tipo, x, y)  -> x, y são só para o desenho
NOS = {
    "R": ("Reservatório", "reservatório", 0, 1),
    "A": ("Estação de bombeamento", "bombeamento", 2, 1),
    "B": ("Ponto B", "intermediário", 4, 2),
    "C": ("Ponto C", "intermediário", 4, 0),
    "D": ("Setor D", "setor", 6, 2),
    "E": ("Setor E", "setor", 6, 0),
    "F": ("Setor F", "setor", 8, 1),
    "G": ("Setor G", "setor", 10, 1),
}
TUBOS = [
    ("R", "A", 2), ("A", "B", 2), ("A", "C", 3), ("B", "D", 2), ("B", "E", 5),
    ("C", "D", 6), ("C", "E", 4), ("D", "F", 2), ("E", "F", 3), ("F", "G", 2),
]

# Resultados fixos só para R -> G (chave = tubulação desativada ou None)
RESULTADOS_EXEMPLO = {
    None: {"caminho": ["R", "A", "B", "D", "F", "G"], "dist": 10,
           "inacessiveis": [], "pontes": [("R", "A"), ("F", "G")]},
    ("B", "D"): {"caminho": ["R", "A", "B", "E", "F", "G"], "dist": 14,
                 "inacessiveis": [], "pontes": [("R", "A"), ("F", "G")]},
    ("R", "A"): {"caminho": None, "dist": None,
                 "inacessiveis": ["A", "B", "C", "D", "E", "F", "G"],
                 "pontes": [("F", "G")]},
    ("F", "G"): {"caminho": None, "dist": None,
                 "inacessiveis": ["G"], "pontes": [("R", "A")]},
}


def resultado_exemplo(origem, destino, falha):
    """Provisório. Trocar pela chamada real da pessoa 5."""
    if (origem, destino) != ("R", "G"):
        return None
    return RESULTADOS_EXEMPLO.get(falha)


# ---------- Desenho ----------
def desenhar(falha, res):
    fig, ax = plt.subplots(figsize=(10, 4))
    caminho = res["caminho"] if res else None
    arestas_caminho = set()
    if caminho:
        arestas_caminho = {frozenset(p) for p in zip(caminho, caminho[1:])}
    pontes = {frozenset(p) for p in res["pontes"]} if res else set()
    inacessiveis = set(res["inacessiveis"]) if res else set()

    for u, v, d in TUBOS:
        x = [NOS[u][2], NOS[v][2]]
        y = [NOS[u][3], NOS[v][3]]
        chave = frozenset((u, v))
        if falha and chave == frozenset(falha):
            cor, estilo, larg = "red", "--", 2
        elif chave in arestas_caminho:
            cor, estilo, larg = "green", "-", 4
        elif chave in pontes:
            cor, estilo, larg = "orange", "-", 2.5
        else:
            cor, estilo, larg = "gray", "-", 1.5
        ax.plot(x, y, color=cor, linestyle=estilo, linewidth=larg, zorder=1)
        ax.text(sum(x) / 2, sum(y) / 2 + 0.12, f"{d} km", ha="center", fontsize=8)

    for id_, (_, _, x, y) in NOS.items():
        cor = "lightgray" if id_ in inacessiveis else "lightskyblue"
        ax.scatter(x, y, s=700, color=cor, edgecolor="black", zorder=2)
        ax.text(x, y, id_, ha="center", va="center", fontweight="bold", zorder=3)

    # legenda
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([0], [0], color="green", lw=4, label="Menor caminho"),
        Line2D([0], [0], color="orange", lw=2.5, label="Ponte (tubulação crítica)"),
        Line2D([0], [0], color="red", lw=2, ls="--", label="Tubulação quebrada"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="lightgray",
               markeredgecolor="black", markersize=10, label="Ponto inacessível"),
    ], loc="upper center", bbox_to_anchor=(0.5, -0.02), ncol=4, fontsize=8, frameon=False)
    ax.set_axis_off()
    ax.set_xlim(-1, 11)
    ax.set_ylim(-0.7, 2.7)
    return fig


# ---------- Tela ----------
st.set_page_config(page_title="Rede de água", layout="wide")
st.title("Monitoramento de distribuição de água")
st.warning("Modo desenvolvimento: resultados FIXOS de exemplo (só R → G).")

if "falha" not in st.session_state:
    st.session_state.falha = None  # None = rede original

ids = list(NOS.keys())
with st.sidebar:
    st.header("Controles")
    origem = st.selectbox("Origem", ids, index=ids.index("R"))
    destino = st.selectbox("Destino", ids, index=ids.index("G"))
    opcoes = [f"{u}–{v}" for u, v, _ in TUBOS]
    escolhida = st.selectbox("Tubulação a interromper", opcoes)
    if st.button("Simular falha", type="primary"):
        u, v = escolhida.split("–")
        st.session_state.falha = (u, v)
    if st.button("Restaurar rede"):
        st.session_state.falha = None

falha = st.session_state.falha
res = resultado_exemplo(origem, destino, falha)

if falha:
    st.error(f"Tubulação interrompida: {falha[0]}–{falha[1]}")
else:
    st.success("Rede original (sem falhas)")

col1, col2 = st.columns([3, 1])
with col1:
    st.pyplot(desenhar(falha, res))
with col2:
    st.subheader("Resultados")
    if res is None:
        st.info("Sem resultado de exemplo para essa origem/destino.")
    elif res["caminho"] is None:
        st.error("Sem caminho entre origem e destino.")
    else:
        st.metric("Distância", f"{res['dist']} km")
        st.write("Caminho: " + " → ".join(res["caminho"]))
    if res:
        st.write("Pontos inacessíveis: " +
                 (", ".join(res["inacessiveis"]) or "nenhum"))
        st.write("Pontes: " + ", ".join(f"{u}–{v}" for u, v in res["pontes"]))
