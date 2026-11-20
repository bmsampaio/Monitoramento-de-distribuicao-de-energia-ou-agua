"""Teste de integração da rede R9 com Dijkstra, BFS e Tarjan.

Coloque na raiz do projeto, ao lado de modelos/, algoritmos/ e dados/.
Execute: python testar_integracao_r9.py

Não altera os arquivos nem a rede original.
"""
import csv
from pathlib import Path
from math import isclose

from modelos.no import No
from modelos.tubulacao import Tubulacao
from modelos.rede import Rede
from algoritmos.dijkstra import dijkstra
from algoritmos.bfs import bfs
from algoritmos.pontes import encontrar_pontes

RAIZ = Path(__file__).resolve().parent


def carregar_rede_csv(pasta_dados=RAIZ / 'dados'):
    """Carregamento de teste, provisório até integrar leitura_csv.py da Pessoa 1."""
    rede = Rede()
    with (pasta_dados / 'nos.csv').open(encoding='utf-8-sig', newline='') as arquivo:
        for row in csv.DictReader(arquivo):
            rede.adicionar_no(No(row['id'].strip(), row['nome'].strip(), row['tipo'].strip()))

    with (pasta_dados / 'tubulacoes.csv').open(encoding='utf-8-sig', newline='') as arquivo:
        for row in csv.DictReader(arquivo):
            status = row['ativa'].strip().lower()
            if status not in ('true', 'false'):
                raise ValueError(f"Estado inválido para tubulação {row['id']}: {status}")
            rede.adicionar_tubulacao(Tubulacao(
                row['id'].strip(), row['origem'].strip(), row['destino'].strip(),
                float(row['distancia_km']), status == 'true'
            ))
    return rede


def validar_caminho(rede, caminho, distancia):
    """Confere se o caminho usa arestas ativas e se o peso somado é correto."""
    if not caminho:
        assert distancia is None
        return
    total = 0.0
    for origem, destino in zip(caminho, caminho[1:]):
        vizinhos = dict(rede.vizinhos_ativos(origem))
        assert destino in vizinhos, f"Trecho ausente/inativo: {origem} -> {destino}"
        total += vizinhos[destino]
    assert isclose(total, distancia, abs_tol=1e-8), (total, distancia)


def testar_tudo():
    original = carregar_rede_csv()
    assert len(original.vertices) == 62, f"Esperados 62 nós; recebi {len(original.vertices)}"
    assert len(original.tubulacoes) == 72, f"Esperadas 72 tubulações; recebi {len(original.tubulacoes)}"
    print('[OK] CSV carregado: 62 pontos e 72 tubulações')

    # Rede normal
    conectados = bfs(original, 'R')
    assert len(conectados) == 62
    caminho, distancia = dijkstra(original, 'R', '20')
    assert isclose(distancia, 7.635, abs_tol=1e-9), distancia
    validar_caminho(original, caminho, distancia)
    print(f'[OK] Dijkstra R -> 20: {distancia:.3f} km; rota: {" -> ".join(caminho)}')

    pontes = encontrar_pontes(original)
    assert set(pontes) == {'T1', 'T8'}, pontes
    print(f'[OK] BFS: 62 alcançáveis; pontes: {pontes}')

    # Falha T1: isola reservatório
    copia_t1 = original.copiar()
    copia_t1.alterar_estado('T1', False)
    assert bfs(copia_t1, 'R') == ['R']
    assert dijkstra(copia_t1, 'R', '20') == ([], None)
    assert original.tubulacoes['T1'].ativa is True
    print('[OK] T1 inativa: R isolado e rede original preservada')

    # Falha T8: desconecta setor específico, mas não toda rede
    copia_t8 = original.copiar()
    copia_t8.alterar_estado('T8', False)
    conectados_t8 = bfs(copia_t8, 'R')
    assert len(conectados_t8) == 42, len(conectados_t8)
    assert len(set(original.vertices) - set(conectados_t8)) == 20
    assert original.tubulacoes['T8'].ativa is True
    print('[OK] T8 inativa: 42 pontos alcançáveis, 20 desconectados')

    # Origem igual ao destino
    assert dijkstra(original, 'R', 'R') == (['R'], 0)
    print('[OK] Dijkstra origem igual ao destino')
    print('\nTODOS OS TESTES PASSARAM!')


if __name__ == '__main__':
    testar_tudo()
