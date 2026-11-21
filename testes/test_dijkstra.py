"""Testes do Dijkstra (algoritmos/dijkstra.py) com a Rede real.

Rodar na raiz: python -m unittest testes.test_dijkstra -v
"""

import unittest

from algoritmos.dijkstra import dijkstra
from testes.auxiliares import criar_rede_exemplo, montar_rede, retrato_da_rede


def sem(rede, id_tubulacao):
    """Cópia da rede com a tubulação desativada."""
    copia = rede.copiar()
    copia.alterar_estado(id_tubulacao, False)
    return copia


class TestRedeExemplo(unittest.TestCase):
    def setUp(self):
        self.rede = criar_rede_exemplo()

    def test_rede_original_10_km(self):
        self.assertEqual(
            dijkstra(self.rede, "R", "G"), (["R", "A", "B", "D", "F", "G"], 10)
        )

    def test_sem_b_d_14_km_com_rota_empatada(self):
        caminho, distancia = dijkstra(sem(self.rede, "T04"), "R", "G")
        self.assertEqual(distancia, 14)
        self.assertIn(
            caminho,
            [["R", "A", "B", "E", "F", "G"], ["R", "A", "C", "E", "F", "G"]],
        )

    def test_sem_r_a_destino_inacessivel(self):
        self.assertEqual(dijkstra(sem(self.rede, "T01"), "R", "G"), ([], None))

    def test_sem_f_g_destino_inacessivel(self):
        self.assertEqual(dijkstra(sem(self.rede, "T10"), "R", "G"), ([], None))

    def test_origem_igual_ao_destino(self):
        self.assertEqual(dijkstra(self.rede, "R", "R"), (["R"], 0))

    def test_sentido_inverso(self):
        self.assertEqual(
            dijkstra(self.rede, "G", "R"), (["G", "F", "D", "B", "A", "R"], 10)
        )

    def test_nao_altera_a_rede(self):
        antes = retrato_da_rede(self.rede)
        dijkstra(self.rede, "R", "G")
        self.assertEqual(retrato_da_rede(self.rede), antes)

    def test_ponto_inexistente(self):
        for origem, destino in (("Z", "G"), ("R", "Z")):
            with self.subTest(origem=origem, destino=destino):
                with self.assertRaises(ValueError):
                    dijkstra(self.rede, origem, destino)


class TestOutrasRedes(unittest.TestCase):
    def test_rota_com_mais_trechos_pode_ser_mais_curta(self):
        # Direto A-C tem 10 km; por B são 1 + 1 = 2 km.
        rede = montar_rede(
            ["A", "B", "C"],
            [("T1", "A", "C", 10), ("T2", "A", "B", 1), ("T3", "B", "C", 1)],
        )
        self.assertEqual(dijkstra(rede, "A", "C"), (["A", "B", "C"], 2))

    def test_rede_desconexa(self):
        rede = montar_rede(
            ["A", "B", "C", "D"], [("T1", "A", "B", 1), ("T2", "C", "D", 1)]
        )
        self.assertEqual(dijkstra(rede, "A", "D"), ([], None))

    def test_ponto_isolado(self):
        rede = montar_rede(["A", "B"], [])
        self.assertEqual(dijkstra(rede, "A", "B"), ([], None))

    def test_distancias_decimais(self):
        rede = montar_rede(
            ["R", "1", "2"], [("T1", "R", "1", 0.35), ("T2", "1", "2", 1.14)]
        )
        caminho, distancia = dijkstra(rede, "R", "2")
        self.assertEqual(caminho, ["R", "1", "2"])
        self.assertAlmostEqual(distancia, 1.49)


if __name__ == "__main__":
    unittest.main()
