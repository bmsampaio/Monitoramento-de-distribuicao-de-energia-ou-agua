"""Lê resultados_desempenho_dijkstra.csv e gera PNG para o relatório.

Execute após o benchmark, na raiz: python -m desempenho.gerar_grafico_desempenho
Lê e grava nesta pasta. Requer matplotlib (requirements.txt).
"""
import csv
from pathlib import Path

import matplotlib.pyplot as plt

RAIZ = Path(__file__).resolve().parent
ENTRADA = RAIZ / 'resultados_desempenho_dijkstra.csv'
SAIDA = RAIZ / 'grafico_desempenho_dijkstra.png'

with ENTRADA.open(encoding='utf-8-sig', newline='') as arquivo:
    dados = list(csv.DictReader(arquivo))

rotulos = [f"R9\n({r['vertices']} V)" if r['tipo'].startswith('R9') else
           f"{r['vertices']} V\n{r['arestas']} E" for r in dados]
valores = [float(r['mediana_ms']) for r in dados]

fig, ax = plt.subplots(figsize=(9, 4.8))
barras = ax.bar(rotulos, valores)
ax.set_title('Desempenho do Dijkstra — mediana de 30 execuções')
ax.set_ylabel('Tempo de execução (ms)')
ax.set_xlabel('Grafo (V = vértices; E = arestas)')
ax.grid(axis='y', alpha=0.2)
ax.set_axisbelow(True)
ax.bar_label(barras, labels=[f'{v:.3f}' for v in valores], padding=4, fontsize=9)
ax.set_ylim(0, max(valores) * 1.2)
fig.tight_layout()
fig.savefig(SAIDA, dpi=180)
plt.close(fig)
print('Gráfico gerado:', SAIDA)
