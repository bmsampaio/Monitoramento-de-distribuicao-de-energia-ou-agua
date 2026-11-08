"""Testes da busca em largura (algoritmos/bfs.py).

Cada teste monta uma rede nova, então as falhas simuladas em um teste não
se acumulam nos outros.
"""

import unittest

from algoritmos.bfs import bfs
from testes.auxiliares import (
    criar_rede_exemplo,
    montar_rede,
    rede_por_pares,
    retrato_da_rede,
)

TODOS_OS_PONTOS = {"R", "A", "B", "C", "D", "E", "F", "G"}


class TestBfsRedeExemplo(unittest.TestCase):
    """Resultados esperados da BFS na rede de exemplo (README, seção 8)."""

    def setUp(self):
        """Cria uma rede de exemplo nova, com as 10 tubulações ativas."""
        self.rede = criar_rede_exemplo()

    def test_rede_original_alcanca_os_oito_pontos(self):
        """Rede original: a BFS a partir de R alcança os 8 pontos.

        Cenário: rede de exemplo sem alterações, BFS a partir de R.
        Esperado: os 8 pontos, cada um uma única vez, com R em primeiro.
        Por quê: a rede é conexa. R-A liga o reservatório a A, e de A se
        chega a todos os outros pontos, por exemplo por R-A-B-D-F-G até o
        setor G.
        """
        resultado = bfs(self.rede, "R")

        self.assertEqual(resultado[0], "R")
        self.assertEqual(len(resultado), 8)
        self.assertEqual(set(resultado), TODOS_OS_PONTOS)

    def test_ordem_de_visita_segue_as_camadas(self):
        """A ordem do resultado é a ordem de visita, camada por camada.

        Cenário: rede de exemplo sem alterações, BFS a partir de R.
        Esperado: R; depois A; depois B e C; depois D e E; depois F; por
        último G.
        Por quê: a camada de um ponto é o menor número de tubulações entre
        ele e R. A está a 1 (R-A), B e C a 2 (via A), D e E a 3 (via B ou
        C), F a 4 e G a 5. A BFS visita uma camada inteira antes de passar à
        seguinte. Dentro da mesma camada, a ordem depende da ordem de
        cadastro, por isso o teste não a fixa.
        """
        resultado = bfs(self.rede, "R")

        self.assertEqual(resultado[:2], ["R", "A"])
        self.assertEqual(set(resultado[2:4]), {"B", "C"})
        self.assertEqual(set(resultado[4:6]), {"D", "E"})
        self.assertEqual(resultado[6:], ["F", "G"])

    def test_desativar_b_d_mantem_todos_alcancaveis(self):
        """Sem B-D, todos os pontos continuam alcançáveis a partir de R.

        Cenário: rede de exemplo com B-D (T04) desativada.
        Esperado: os mesmos 8 pontos da rede original.
        Por quê: B-D faz parte de um ciclo (A-B-D-C-A). B continua ligado a
        A por A-B, e D continua ligado por C-D e D-F. A falha só alonga
        caminhos (R→G passa de 10 para 14 km, o que é assunto do Dijkstra),
        mas não desliga nenhum ponto.
        """
        self.rede.alterar_estado("T04", False)

        resultado = bfs(self.rede, "R")

        self.assertEqual(len(resultado), 8)
        self.assertEqual(set(resultado), TODOS_OS_PONTOS)

    def test_desativar_r_a_deixa_so_o_reservatorio(self):
        """Sem R-A, a BFS a partir de R devolve só R.

        Cenário: rede de exemplo com R-A (T01) desativada.
        Esperado: bfs(rede, "R") == ["R"]; os outros sete pontos, incluindo
        os quatro setores D, E, F e G, ficam inacessíveis. A partir de A,
        esses sete continuam ligados entre si.
        Por quê: R-A é a única tubulação de R. Sem ela, R não tem vizinhos
        ativos. A falha não quebra o restante da rede, só o separa do
        reservatório, e é isso que a BFS a partir de A confirma.
        """
        self.rede.alterar_estado("T01", False)

        self.assertEqual(bfs(self.rede, "R"), ["R"])
        self.assertEqual(set(bfs(self.rede, "A")), TODOS_OS_PONTOS - {"R"})

    def test_desativar_f_g_isola_g(self):
        """Sem F-G, o setor G fica inacessível a partir de R.

        Cenário: rede de exemplo com F-G (T10) desativada.
        Esperado: os 7 pontos de R a F, sem G.
        Por quê: F-G é a única tubulação de G. Os demais pontos continuam
        ligados a R pelos mesmos caminhos de antes.
        """
        self.rede.alterar_estado("T10", False)

        resultado = bfs(self.rede, "R")

        self.assertNotIn("G", resultado)
        self.assertEqual(set(resultado), TODOS_OS_PONTOS - {"G"})

    def test_nao_altera_a_rede(self):
        """A BFS não altera a rede recebida.

        Cenário: rede de exemplo com B-D (T04) desativada, para haver
        tubulações nos dois estados; BFS a partir de R e a partir de G.
        Esperado: pontos, tubulações (inclusive o campo ativa) e adjacência
        idênticos antes e depois.
        Por quê: a BFS só consulta a rede. A simulação de falhas depende
        disso para comparar o antes e o depois a partir da mesma rede.
        """
        self.rede.alterar_estado("T04", False)
        antes = retrato_da_rede(self.rede)

        bfs(self.rede, "R")
        bfs(self.rede, "G")

        self.assertEqual(retrato_da_rede(self.rede), antes)


class TestBfsCasosGerais(unittest.TestCase):
    """Casos gerais: tubulação inativa, rede desconexa, entradas extremas."""

    def test_tubulacao_inativa_e_ignorada(self):
        """Uma tubulação inativa não é usada como caminho pela BFS.

        Cenário: linha A-B-C, com B-C (T02) desativada; depois T02 é
        reativada.
        Esperado: com T02 inativa, só A e B; depois de reativá-la, A, B e C.
        Por quê: desativar não apaga a tubulação (ela continua em
        rede.adjacencia), mas rede.vizinhos_ativos a omite, então C fica sem
        ligação ativa com A. Reativar mostra que o resultado depende só do
        estado atual das tubulações.
        """
        rede = rede_por_pares("A-B B-C")
        rede.alterar_estado("T02", False)

        self.assertIn("C", rede.adjacencia["B"])
        self.assertEqual(bfs(rede, "A"), ["A", "B"])

        rede.alterar_estado("T02", True)

        self.assertEqual(bfs(rede, "A"), ["A", "B", "C"])

    def test_rede_desconexa_alcanca_so_a_componente_da_origem(self):
        """Em uma rede desconexa, a BFS fica na componente da origem.

        Cenário: duas componentes sem tubulação entre elas, o triângulo
        A-B-C e o par X-Y.
        Esperado: a partir de A, só A, B e C; a partir de X, só X e Y.
        Por quê: não existe nenhuma tubulação, ativa ou não, ligando as duas
        componentes, então nenhum caminho sai de uma e chega à outra.
        """
        rede = rede_por_pares("A-B B-C C-A X-Y")

        self.assertEqual(set(bfs(rede, "A")), {"A", "B", "C"})
        self.assertEqual(set(bfs(rede, "X")), {"X", "Y"})

    def test_ponto_unico_sem_tubulacoes(self):
        """Em uma rede com um único ponto, a BFS devolve só esse ponto.

        Cenário: rede com o ponto P e nenhuma tubulação.
        Esperado: ["P"].
        Por quê: a origem sempre é alcançável a partir de si mesma, e P não
        tem vizinhos.
        """
        rede = montar_rede(["P"], [])

        self.assertEqual(bfs(rede, "P"), ["P"])

    def test_origem_inexistente_levanta_value_error(self):
        """Uma origem que não está na rede levanta ValueError.

        Cenário: rede de exemplo, BFS a partir de "Z", que não foi
        cadastrado.
        Esperado: ValueError com o ID "Z" na mensagem.
        Por quê: uma origem desconhecida é erro de entrada, e não "nenhum
        ponto alcançável". Devolver uma lista vazia esconderia, por
        exemplo, um erro de digitação no ID.
        """
        rede = criar_rede_exemplo()

        with self.assertRaises(ValueError) as contexto:
            bfs(rede, "Z")

        self.assertIn("'Z'", str(contexto.exception))
