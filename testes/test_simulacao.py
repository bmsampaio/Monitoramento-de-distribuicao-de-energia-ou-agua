"""Testes de integração da simulação de falhas (servicos/simulacao.py).

Conferem os cenários da página 6 do plano passando pelos módulos reais:
Rede, BFS, Dijkstra e pontes. Cada cenário começa da rede original.

Rodar na raiz: python -m unittest testes.test_simulacao -v
"""

import unittest

from servicos.simulacao import simular_falha, simular_falhas
from testes.auxiliares import criar_rede_exemplo, retrato_da_rede

TODOS = ["R", "A", "B", "C", "D", "E", "F", "G"]


class TestCenariosDoPlano(unittest.TestCase):
    def setUp(self):
        self.rede = criar_rede_exemplo()

    def test_rede_original(self):
        r = simular_falha(self.rede, "R", "G", None)
        self.assertFalse(r["falha_aplicada"])
        self.assertEqual(r["antes"]["alcancaveis"], TODOS)
        self.assertEqual(r["caminho_antes"], ["R", "A", "B", "D", "F", "G"])
        self.assertEqual(r["distancia_antes"], 10)
        self.assertEqual(r["pontes_antes"], ["T01", "T10"])
        self.assertEqual(r["distancia_depois"], 10)
        self.assertEqual(r["inacessiveis_apos_falha"], [])

    def test_falha_b_d(self):
        r = simular_falha(self.rede, "R", "G", "T04")
        self.assertTrue(r["falha_aplicada"])
        self.assertCountEqual(r["depois"]["alcancaveis"], TODOS)
        self.assertEqual(r["distancia_depois"], 14)
        self.assertIn(
            r["caminho_depois"],
            [["R", "A", "B", "E", "F", "G"], ["R", "A", "C", "E", "F", "G"]],
        )
        self.assertEqual(r["inacessiveis_apos_falha"], [])

    def test_falha_r_a(self):
        r = simular_falha(self.rede, "R", "G", "T01")
        self.assertEqual(r["depois"]["alcancaveis"], ["R"])
        self.assertEqual(
            r["inacessiveis_apos_falha"], ["A", "B", "C", "D", "E", "F", "G"]
        )
        self.assertIsNone(r["caminho_depois"])
        self.assertIsNone(r["distancia_depois"])

    def test_falha_f_g(self):
        r = simular_falha(self.rede, "R", "G", "T10")
        self.assertEqual(r["inacessiveis_apos_falha"], ["G"])
        self.assertIsNone(r["distancia_depois"])
        # T10 inativa deixa de ser ponte.
        self.assertEqual(r["pontes_nao_sao_mais"], ["T10"])

    def test_restaurar_volta_ao_inicio(self):
        simular_falha(self.rede, "R", "G", "T04")
        r = simular_falha(self.rede, "R", "G", None)
        self.assertEqual(r["distancia_depois"], 10)
        self.assertEqual(r["caminho_depois"], ["R", "A", "B", "D", "F", "G"])


class TestComparacao(unittest.TestCase):
    def setUp(self):
        self.rede = criar_rede_exemplo()

    def test_nao_altera_a_rede_original(self):
        antes = retrato_da_rede(self.rede)
        for tubulacao in self.rede.tubulacoes:
            simular_falha(self.rede, "R", "G", tubulacao)
        self.assertEqual(retrato_da_rede(self.rede), antes)

    def test_falha_cria_ponte_nova(self):
        # Sem D-F, E-F passa a ser a única ligação de F com o resto.
        r = simular_falha(self.rede, "R", "G", "T08")
        self.assertEqual(r["novas_pontes"], ["T09"])
        self.assertEqual(r["pontes_depois"], ["T01", "T09", "T10"])

    def test_origem_igual_ao_destino(self):
        r = simular_falha(self.rede, "R", "R", "T01")
        self.assertEqual(r["caminho_depois"], ["R"])
        self.assertEqual(r["distancia_depois"], 0)

    def test_entradas_invalidas(self):
        for origem, destino, tubulacao in (
            ("Z", "G", None), ("R", "Z", None), ("R", "G", "T99"),
        ):
            with self.subTest(origem=origem, destino=destino, tubulacao=tubulacao):
                with self.assertRaises(ValueError):
                    simular_falha(self.rede, origem, destino, tubulacao)

    def test_uma_falha_informa_a_tubulacao(self):
        r = simular_falha(self.rede, "R", "G", "T04")
        self.assertEqual(r["tubulacao_interrompida"], "T04")
        self.assertEqual(r["tubulacoes_interrompidas"], ["T04"])


class TestFalhasMultiplas(unittest.TestCase):
    def setUp(self):
        self.rede = criar_rede_exemplo()

    def test_sem_b_d_e_c_e_ainda_ha_rota(self):
        r = simular_falhas(self.rede, "R", "G", ["T04", "T07"])
        self.assertEqual(r["tubulacoes_interrompidas"], ["T04", "T07"])
        self.assertEqual(r["caminho_depois"], ["R", "A", "B", "E", "F", "G"])
        self.assertEqual(r["distancia_depois"], 14)
        self.assertEqual(r["inacessiveis_apos_falha"], [])

    def test_sem_b_d_e_b_e_rota_passa_por_c(self):
        # Com as duas saídas de B fechadas, a rota de 14 km fica só por C.
        r = simular_falhas(self.rede, "R", "G", ["T04", "T05"])
        self.assertEqual(r["caminho_depois"], ["R", "A", "C", "E", "F", "G"])
        self.assertEqual(r["distancia_depois"], 14)
        self.assertEqual(r["inacessiveis_apos_falha"], [])

    def test_sem_d_f_e_e_f_isola_f_e_g(self):
        # Nenhuma das duas é ponte sozinha, mas juntas cortam F e G.
        r = simular_falhas(self.rede, "R", "G", ["T08", "T09"])
        self.assertEqual(r["inacessiveis_apos_falha"], ["F", "G"])
        self.assertIsNone(r["caminho_depois"])
        self.assertIsNone(r["distancia_depois"])

    def test_lista_vazia_nao_aplica_falha(self):
        r = simular_falhas(self.rede, "R", "G", [])
        self.assertFalse(r["falha_aplicada"])
        self.assertEqual(r["tubulacoes_interrompidas"], [])
        self.assertEqual(r["distancia_depois"], 10)

    def test_ids_repetidos_contam_uma_vez(self):
        r = simular_falhas(self.rede, "R", "G", ["T04", "T04"])
        self.assertEqual(r["tubulacoes_interrompidas"], ["T04"])
        self.assertEqual(r["distancia_depois"], 14)

    def test_nao_altera_a_rede_original(self):
        antes = retrato_da_rede(self.rede)
        simular_falhas(self.rede, "R", "G", ["T01", "T04", "T10"])
        self.assertEqual(retrato_da_rede(self.rede), antes)

    def test_tubulacao_inexistente_na_lista(self):
        with self.assertRaises(ValueError) as contexto:
            simular_falhas(self.rede, "R", "G", ["T04", "T99"])
        self.assertIn("'T99'", str(contexto.exception))

    def test_texto_em_vez_de_lista(self):
        with self.assertRaises(TypeError):
            simular_falhas(self.rede, "R", "G", "T04")


if __name__ == "__main__":
    unittest.main()
