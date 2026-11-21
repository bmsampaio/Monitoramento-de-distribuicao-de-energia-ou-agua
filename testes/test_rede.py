"""Testes da estrutura da rede: modelos No, Tubulacao e Rede.

Rodar na raiz: python -m unittest testes.test_rede -v
"""

import unittest

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao


def rede_r1():
    """Rede com o reservatório R, o ponto 1 e a tubulação T1 (R-1, 2.54 km)."""
    rede = Rede()
    rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
    rede.adicionar_no(No("1", "Ponto de demanda 1", "ponto_demanda"))
    rede.adicionar_tubulacao(Tubulacao("T1", "R", "1", 2.54))
    return rede


class TestCadastro(unittest.TestCase):
    def test_cadastro_do_reservatorio(self):
        rede = Rede()
        rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
        self.assertIn("R", rede.vertices)
        self.assertEqual(rede.adjacencia["R"], {})

    def test_conexao_nos_dois_sentidos(self):
        rede = rede_r1()
        self.assertEqual(rede.adjacencia["R"]["1"], "T1")
        self.assertEqual(rede.adjacencia["1"]["R"], "T1")
        self.assertEqual(len(rede.tubulacoes), 1)
        self.assertEqual(rede.vizinhos_ativos("R"), [("1", 2.54)])
        self.assertEqual(rede.vizinhos_ativos("1"), [("R", 2.54)])

    def test_rejeita_no_duplicado(self):
        rede = rede_r1()
        with self.assertRaises(ValueError):
            rede.adicionar_no(No("R", "Outro", "reservatorio"))

    def test_rejeita_tubulacao_com_id_duplicado(self):
        rede = rede_r1()
        rede.adicionar_no(No("2", "Ponto 2", "ponto_demanda"))
        with self.assertRaises(ValueError):
            rede.adicionar_tubulacao(Tubulacao("T1", "1", "2", 1.0))

    def test_rejeita_destino_inexistente(self):
        rede = Rede()
        rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
        with self.assertRaises(ValueError) as contexto:
            rede.adicionar_tubulacao(Tubulacao("T1", "R", "X", 2.54))
        self.assertEqual(str(contexto.exception), "O nó de destino não existe.")
        self.assertEqual(rede.tubulacoes, {})
        self.assertEqual(rede.adjacencia["R"], {})

    def test_rejeita_origem_inexistente(self):
        rede = Rede()
        rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
        with self.assertRaises(ValueError):
            rede.adicionar_tubulacao(Tubulacao("T1", "X", "R", 2.54))

    def test_rejeita_laco(self):
        rede = Rede()
        rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
        with self.assertRaises(ValueError):
            rede.adicionar_tubulacao(Tubulacao("T1", "R", "R", 1.0))

    def test_rejeita_distancia_zero_ou_negativa(self):
        for distancia in (0, -2.0):
            with self.subTest(distancia=distancia):
                rede = Rede()
                rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
                rede.adicionar_no(No("1", "Ponto 1", "ponto_demanda"))
                with self.assertRaises(ValueError):
                    rede.adicionar_tubulacao(Tubulacao("T1", "R", "1", distancia))

    def test_rejeita_conexao_duplicada_invertida(self):
        rede = rede_r1()
        with self.assertRaises(ValueError) as contexto:
            rede.adicionar_tubulacao(Tubulacao("T2", "1", "R", 2.54))
        self.assertEqual(
            str(contexto.exception), "Já existe uma tubulação entre esses nós."
        )
        self.assertEqual(len(rede.tubulacoes), 1)
        self.assertEqual(rede.adjacencia["R"]["1"], "T1")
        self.assertEqual(rede.adjacencia["1"]["R"], "T1")


class TestEstado(unittest.TestCase):
    def test_desativar_e_reativar(self):
        rede = rede_r1()
        rede.alterar_estado("T1", False)
        self.assertIn("T1", rede.tubulacoes)
        self.assertEqual(rede.vizinhos_ativos("R"), [])
        self.assertEqual(rede.vizinhos_ativos("1"), [])

        rede.alterar_estado("T1", True)
        self.assertEqual(rede.vizinhos_ativos("R"), [("1", 2.54)])
        self.assertEqual(rede.vizinhos_ativos("1"), [("R", 2.54)])

    def test_vizinhos_de_no_inexistente(self):
        with self.assertRaises(ValueError):
            rede_r1().vizinhos_ativos("X")

    def test_alterar_tubulacao_inexistente(self):
        with self.assertRaises(ValueError):
            rede_r1().alterar_estado("T9", False)


class TestCopia(unittest.TestCase):
    def test_copia_independente(self):
        rede = rede_r1()
        copia = rede.copiar()
        copia.alterar_estado("T1", False)
        self.assertEqual(copia.vizinhos_ativos("R"), [])
        self.assertEqual(rede.vizinhos_ativos("R"), [("1", 2.54)])

    def test_copia_tem_objetos_novos(self):
        rede = rede_r1()
        copia = rede.copiar()
        self.assertEqual(set(copia.vertices), set(rede.vertices))
        self.assertEqual(set(copia.tubulacoes), set(rede.tubulacoes))
        self.assertIsNot(copia.vertices["R"], rede.vertices["R"])
        self.assertIsNot(copia.tubulacoes["T1"], rede.tubulacoes["T1"])

    def test_copia_preserva_estado_inativo(self):
        rede = rede_r1()
        rede.alterar_estado("T1", False)
        self.assertFalse(rede.copiar().tubulacoes["T1"].ativa)

    def test_copia_de_rede_vazia(self):
        copia = Rede().copiar()
        self.assertEqual(copia.vertices, {})
        self.assertEqual(copia.tubulacoes, {})


if __name__ == "__main__":
    unittest.main()
