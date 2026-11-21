"""Testes do carregamento dos CSVs (servicos/leitura_csv.py).

Rodar na raiz: python -m unittest testes.test_leitura_csv -v
"""

import tempfile
import unittest
from pathlib import Path

from servicos.leitura_csv import carregar_nos, carregar_rede, carregar_tubulacoes
from modelos.rede import Rede

PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"
NOS_R9 = PASTA_DADOS / "nos.csv"
TUBULACOES_R9 = PASTA_DADOS / "tubulacoes.csv"

NOS_OK = "id,nome,tipo\nR,Reservatório,reservatorio\n1,Ponto 1,ponto_demanda\n"
CABECALHO_TUBOS = "id,origem,destino,distancia_km,ativa\n"


class TestBaseR9(unittest.TestCase):
    def test_carrega_nos(self):
        rede = Rede()
        carregar_nos(rede, NOS_R9)
        self.assertEqual(len(rede.vertices), 62)
        self.assertEqual(rede.vertices["R"].nome, "Reservatório")
        self.assertEqual(rede.adjacencia["R"], {})

    def test_carrega_tubulacoes(self):
        rede = Rede()
        carregar_nos(rede, NOS_R9)
        carregar_tubulacoes(rede, TUBULACOES_R9)
        self.assertEqual(len(rede.tubulacoes), 72)
        self.assertEqual(rede.adjacencia["R"]["1"], "T1")
        self.assertEqual(rede.adjacencia["1"]["R"], "T1")
        self.assertIn(("1", 2.54), rede.vizinhos_ativos("R"))

    def test_carrega_rede_completa(self):
        rede = carregar_rede(NOS_R9, TUBULACOES_R9)
        self.assertEqual(len(rede.vertices), 62)
        self.assertEqual(len(rede.tubulacoes), 72)
        self.assertTrue(all(t.ativa for t in rede.tubulacoes.values()))


class TestEntradasInvalidas(unittest.TestCase):
    """Cada caso grava CSVs temporários e confere a mensagem de erro."""

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)

    def carregar(self, nos, tubulacoes):
        caminho_nos = Path(self.pasta.name) / "nos.csv"
        caminho_tubos = Path(self.pasta.name) / "tubulacoes.csv"
        caminho_nos.write_text(nos, encoding="utf-8")
        caminho_tubos.write_text(tubulacoes, encoding="utf-8")
        return carregar_rede(caminho_nos, caminho_tubos)

    def assertErro(self, trecho, nos, tubulacoes):
        with self.assertRaises(ValueError) as contexto:
            self.carregar(nos, tubulacoes)
        self.assertIn(trecho, str(contexto.exception))

    def test_aceita_espacos_bom_e_estado_maiusculo(self):
        rede = self.carregar(
            "﻿" + NOS_OK, CABECALHO_TUBOS + " T1 , R , 1 , 2.5 , FALSE \n"
        )
        self.assertEqual(rede.adjacencia["R"]["1"], "T1")
        self.assertFalse(rede.tubulacoes["T1"].ativa)
        self.assertEqual(rede.tubulacoes["T1"].distancia, 2.5)

    def test_coluna_faltando(self):
        self.assertErro(
            "faltam as colunas distancia_km",
            NOS_OK, "id,origem,destino,ativa\nT1,R,1,true\n",
        )

    def test_campo_vazio_no_no(self):
        self.assertErro(
            "linha 2: campo vazio em id", "id,nome,tipo\n,Sem ID,ponto\n",
            CABECALHO_TUBOS,
        )

    def test_campo_vazio_na_tubulacao(self):
        self.assertErro(
            "linha 2: campo vazio em distancia_km",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,,true\n",
        )

    def test_linha_com_colunas_a_menos(self):
        self.assertErro(
            "campo vazio em distancia_km, ativa",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1\n",
        )

    def test_distancia_nao_numerica(self):
        self.assertErro(
            "linha 2: distância inválida 'abc'",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,abc,true\n",
        )

    def test_distancia_infinita_ou_nan(self):
        for valor in ("nan", "inf"):
            with self.subTest(valor=valor):
                self.assertErro(
                    "distância inválida",
                    NOS_OK, CABECALHO_TUBOS + f"T1,R,1,{valor},true\n",
                )

    def test_distancia_negativa(self):
        self.assertErro(
            "linha 2: Distância inválida",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,-2,true\n",
        )

    def test_estado_invalido(self):
        self.assertErro(
            "estado inválido 'sim'",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,2,sim\n",
        )

    def test_no_inexistente(self):
        self.assertErro(
            "linha 3: O nó de destino não existe.",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,2,true\nT2,1,9,2,true\n",
        )

    def test_no_repetido(self):
        self.assertErro(
            "linha 4: Já existe um nó",
            NOS_OK + "R,Outro,reservatorio\n", CABECALHO_TUBOS,
        )

    def test_conexao_repetida(self):
        self.assertErro(
            "linha 3: Já existe uma tubulação entre esses nós.",
            NOS_OK, CABECALHO_TUBOS + "T1,R,1,2,true\nT2,1,R,3,true\n",
        )


if __name__ == "__main__":
    unittest.main()
