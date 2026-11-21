"""Teste de integração na base R-9 com Dijkstra, BFS, pontes e simulação.

Carrega os CSVs com servicos/leitura_csv.py e não altera os arquivos.

Rodar na raiz: python -m unittest testes.test_integracao_r9 -v
"""

import unittest
from math import isclose
from pathlib import Path

from algoritmos.bfs import bfs
from algoritmos.dijkstra import dijkstra
from algoritmos.pontes import encontrar_pontes
from servicos.leitura_csv import carregar_rede
from servicos.simulacao import simular_falha, simular_falhas

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"


def carregar_r9():
    return carregar_rede(PASTA_DADOS / "nos.csv", PASTA_DADOS / "tubulacoes.csv")


class TestIntegracaoR9(unittest.TestCase):
    def setUp(self):
        self.rede = carregar_r9()

    def assertCaminhoValido(self, caminho, distancia):
        """Confere se o caminho usa tubulações ativas e se a soma bate."""
        total = 0.0
        for origem, destino in zip(caminho, caminho[1:]):
            vizinhos = dict(self.rede.vizinhos_ativos(origem))
            self.assertIn(destino, vizinhos, f"Trecho ausente: {origem}-{destino}")
            total += vizinhos[destino]
        self.assertTrue(isclose(total, distancia, abs_tol=1e-9), (total, distancia))

    def test_tamanho(self):
        self.assertEqual(len(self.rede.vertices), 62)
        self.assertEqual(len(self.rede.tubulacoes), 72)

    def test_rede_original(self):
        self.assertEqual(len(bfs(self.rede, "R")), 62)
        self.assertEqual(encontrar_pontes(self.rede), ["T1", "T8"])

        caminho, distancia = dijkstra(self.rede, "R", "20")
        self.assertTrue(isclose(distancia, 7.635, abs_tol=1e-9), distancia)
        self.assertEqual(caminho[0], "R")
        self.assertEqual(caminho[-1], "20")
        self.assertCaminhoValido(caminho, distancia)

    def test_falha_t1_isola_o_reservatorio(self):
        copia = self.rede.copiar()
        copia.alterar_estado("T1", False)
        self.assertEqual(bfs(copia, "R"), ["R"])
        self.assertEqual(dijkstra(copia, "R", "20"), ([], None))
        self.assertTrue(self.rede.tubulacoes["T1"].ativa)

    def test_falha_t8_desconecta_20_pontos(self):
        r = simular_falha(self.rede, "R", "20", "T8")
        self.assertEqual(len(r["depois"]["alcancaveis"]), 42)
        self.assertEqual(len(r["inacessiveis_apos_falha"]), 20)
        self.assertTrue(self.rede.tubulacoes["T8"].ativa)

    def test_falhas_t8_e_t1_juntas(self):
        r = simular_falhas(self.rede, "R", "20", ["T8", "T1"])
        self.assertEqual(r["depois"]["alcancaveis"], ["R"])
        self.assertEqual(len(r["inacessiveis_apos_falha"]), 61)
        self.assertIsNone(r["distancia_depois"])

    def test_origem_igual_ao_destino(self):
        self.assertEqual(dijkstra(self.rede, "R", "R"), (["R"], 0))


if __name__ == "__main__":
    unittest.main()
