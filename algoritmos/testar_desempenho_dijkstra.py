"""Medições reproduzíveis do Dijkstra com a classe Rede da Pessoa 1.

Execute: python testar_desempenho_dijkstra.py
Gera resultados_desempenho_dijkstra.csv na mesma pasta.
Os tempos variam entre computadores; use o CSV gerado na SUA máquina no relatório.
"""
import csv
import platform
import random
import statistics
import time
from pathlib import Path

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao
from algoritmos.dijkstra import dijkstra
from testar_integracao_r9 import carregar_rede_csv

RAIZ = Path(__file__).resolve().parent
TAMANHOS = (100, 500, 1000, 5000)
REPETICOES = 30
AQUECIMENTOS = 5
SEMENTE = 2026


def gerar_grafo_conexo(numero_vertices, fator_arestas=3, semente=SEMENTE):
    """Grafo sintético não direcionado, conexo, esparso e com pesos positivos."""
    if numero_vertices < 2:
        raise ValueError('É necessário pelo menos 2 vértices')

    rng = random.Random(semente)
    rede = Rede()
    for i in range(numero_vertices):
        rede.adicionar_no(No(str(i), f'Ponto {i}', 'ponto_demanda'))

    arestas = set()
    proximo_id = 0

    def ligar(a, b):
        nonlocal proximo_id
        if a == b:
            return False  # A classe Rede não aceita laços.
        chave = (min(a, b), max(a, b))
        if chave in arestas:
            return False
        arestas.add(chave)
        proximo_id += 1
        peso = round(rng.uniform(0.1, 10.0), 3)
        rede.adicionar_tubulacao(Tubulacao(f'T{proximo_id}', str(a), str(b), peso))
        return True

    # Cadeia inicial garante conectividade.
    for i in range(numero_vertices - 1):
        ligar(i, i + 1)

    max_arestas = numero_vertices * (numero_vertices - 1) // 2
    alvo = min(fator_arestas * numero_vertices, max_arestas)
    # Conexões extras de alcance local (até 40 índices):
    # aproxima a topologia de uma rede de tubulações e evita "atalhos" globais.
    alcance = min(40, numero_vertices - 1)
    while len(arestas) < alvo:
        a = rng.randrange(numero_vertices)
        deslocamento = rng.randint(1, alcance)
        b = a + deslocamento if a + deslocamento < numero_vertices else a - deslocamento
        ligar(a, b)

    return rede


def medir(rede, origem, destino, repeticoes=REPETICOES):
    # Aquecimento separado das medições.
    for _ in range(AQUECIMENTOS):
        dijkstra(rede, origem, destino)

    tempos_ms = []
    ultimo = None
    for _ in range(repeticoes):
        inicio = time.perf_counter_ns()
        ultimo = dijkstra(rede, origem, destino)
        fim = time.perf_counter_ns()
        tempos_ms.append((fim - inicio) / 1_000_000)

    caminho, distancia = ultimo
    assert caminho and caminho[0] == origem and caminho[-1] == destino
    return {
        'vertices': len(rede.vertices),
        'arestas': len(rede.tubulacoes),
        'repeticoes': repeticoes,
        'mediana_ms': round(statistics.median(tempos_ms), 6),
        'media_ms': round(statistics.mean(tempos_ms), 6),
        'minimo_ms': round(min(tempos_ms), 6),
        'maximo_ms': round(max(tempos_ms), 6),
        'distancia_km': round(distancia, 6)
    }


def executar():
    print('Ambiente:', platform.platform())
    print('Python:', platform.python_version())
    print('Semente:', SEMENTE, '| Repetições por rede:', REPETICOES)
    resultados = []

    r9 = carregar_rede_csv()
    resultados.append({'tipo': 'R9 (dados CSV)', **medir(r9, 'R', '20')})

    for n in TAMANHOS:
        rede = gerar_grafo_conexo(n, semente=SEMENTE + n)
        resultados.append({'tipo': 'Sintético', **medir(rede, '0', str(n - 1))})

    cols = ['tipo', 'vertices', 'arestas', 'repeticoes', 'mediana_ms', 'media_ms',
            'minimo_ms', 'maximo_ms', 'distancia_km']
    saida = RAIZ / 'resultados_desempenho_dijkstra.csv'
    with saida.open('w', encoding='utf-8-sig', newline='') as arq:
        writer = csv.DictWriter(arq, fieldnames=cols)
        writer.writeheader()
        writer.writerows(resultados)

    print('\n{:<17} {:>8} {:>8} {:>13} {:>13}'.format('Rede','V','E','Mediana (ms)','Média (ms)'))
    for r in resultados:
        print('{:<17} {:>8} {:>8} {:>13.6f} {:>13.6f}'.format(
            r['tipo'], r['vertices'], r['arestas'], r['mediana_ms'], r['media_ms']))
    print('\nResultados salvos em:', saida)
    print('Obs.: tempos do relatório devem ser medidos no computador utilizado pelo grupo.')


if __name__ == '__main__':
    executar()
