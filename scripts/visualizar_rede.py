"""Lista os nós e as tubulações da R-9 e gera docs/imagens/rede_r9.dot.

Execute na raiz: python -m scripts.visualizar_rede
A imagem docs/imagens/rede_r9.svg é gerada a partir do .dot com o Graphviz.
"""
from pathlib import Path

from servicos.leitura_csv import carregar_rede

PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "dados"
ARQUIVO_DOT = PASTA_PROJETO / "docs" / "imagens" / "rede_r9.dot"

rede = carregar_rede(PASTA_DADOS / "nos.csv", PASTA_DADOS / "tubulacoes.csv")

print(f"NÓS ({len(rede.vertices)})")
for no in rede.vertices.values():
    print(f"{no.identificador}: {no.nome} ({no.tipo})")

print(f"\nARESTAS ({len(rede.tubulacoes)})")
for tubo in rede.tubulacoes.values():
    estado = "ativa" if tubo.ativa else "inativa"
    print(f"{tubo.identificador}: {tubo.origem} -- {tubo.destino} | {tubo.distancia:.2f} km | {estado}")

with open(ARQUIVO_DOT, "w", encoding="utf-8") as arquivo:
    print("graph R9 {", file=arquivo)
    print('  graph [overlap=false, splines=true];', file=arquivo)
    print('  node [shape=circle, style=filled, fillcolor=lightblue];', file=arquivo)

    for no in rede.vertices.values():
        cor = "gold" if no.tipo == "reservatorio" else "lightblue"
        print(f'  "{no.identificador}" [fillcolor="{cor}"];', file=arquivo)

    for tubo in rede.tubulacoes.values():
        estilo = "solid" if tubo.ativa else "dashed"
        print(f'  "{tubo.origem}" -- "{tubo.destino}" [style={estilo}];', file=arquivo)

    print("}", file=arquivo)

print(f"\nArquivo gerado: {ARQUIVO_DOT}")
