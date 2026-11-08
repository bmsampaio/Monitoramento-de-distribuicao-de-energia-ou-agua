"""Testes da busca de pontes (algoritmos/pontes.py).

Além dos resultados esperados na rede de exemplo e em redes pequenas
(ciclo, árvore, rede desconexa), o resultado do Tarjan é comparado com uma
força bruta que aplica diretamente a definição de ponte. Cada teste monta
uma rede nova, então as falhas simuladas não se acumulam.
"""

import random
import sys
import unittest

from algoritmos.bfs import bfs
from algoritmos.pontes import encontrar_pontes
from testes.auxiliares import (
    criar_rede_exemplo,
    montar_rede,
    rede_por_pares,
    retrato_da_rede,
)


def contar_componentes(rede):
    """Conta as componentes conexas da rede, considerando só tubulações ativas.

    Percorre os pontos e, a cada ponto ainda não alcançado, roda a BFS do
    projeto a partir dele; cada uma dessas buscas descobre uma componente
    inteira. A própria BFS é verificada em test_bfs.py.

    Args:
        rede (Rede): rede analisada. Não é alterada.

    Returns:
        int: número de componentes conexas. Um ponto isolado conta como uma
        componente.
    """
    alcancados = set()
    componentes = 0
    for ponto in rede.vertices:
        if ponto not in alcancados:
            componentes += 1
            alcancados.update(bfs(rede, ponto))
    return componentes


def pontes_por_forca_bruta(rede):
    """Encontra as pontes aplicando diretamente a definição de ponte.

    Para cada tubulação ativa, desativa-a em uma cópia da rede e verifica se
    o número de componentes aumentou. Não usa nenhuma ideia do Tarjan
    (tempos de descoberta, low, pilha), por isso serve de referência
    independente para conferir encontrar_pontes. Custa O(E * (V + E)) e só
    é usada em redes pequenas.

    Args:
        rede (Rede): rede analisada. Não é alterada, porque cada falha é
            aplicada em uma cópia (rede.copiar()).

    Returns:
        list[str]: IDs das pontes, em ordem crescente, no mesmo formato de
        encontrar_pontes.
    """
    componentes_antes = contar_componentes(rede)
    pontes = []
    for identificador, tubulacao in rede.tubulacoes.items():
        if not tubulacao.ativa:
            continue
        copia = rede.copiar()
        copia.alterar_estado(identificador, False)
        if contar_componentes(copia) > componentes_antes:
            pontes.append(identificador)
    return sorted(pontes)


class TestPontesRedeExemplo(unittest.TestCase):
    """Resultados esperados da busca de pontes na rede de exemplo."""

    def setUp(self):
        """Cria uma rede de exemplo nova, com as 10 tubulações ativas."""
        self.rede = criar_rede_exemplo()

    def test_rede_original_tem_pontes_r_a_e_f_g(self):
        """Rede original: as pontes são R-A (T01) e F-G (T10).

        Cenário: rede de exemplo sem alterações.
        Esperado: ["T01", "T10"].
        Por quê: R-A é a única tubulação de R, e F-G é a única de G; retirar
        qualquer uma delas isola um ponto. Todas as outras tubulações estão
        em algum ciclo entre A e F (A-B-D-C-A, B-D-F-E-B ou A-B-E-C-A) e
        por isso têm caminho alternativo.
        """
        self.assertEqual(encontrar_pontes(self.rede), ["T01", "T10"])

    def test_tubulacao_inativa_nao_e_apontada_como_ponte(self):
        """Uma tubulação inativa não aparece como ponte.

        Cenário: rede de exemplo com R-A (T01) desativada.
        Esperado: ["T10"].
        Por quê: ponte é uma tubulação ativa cuja retirada separa a rede.
        R-A já está fora de operação e R já ficou isolado, então não há o
        que retirar. Entre os pontos restantes, F-G continua sendo a única
        ligação de G.
        """
        self.rede.alterar_estado("T01", False)

        self.assertEqual(encontrar_pontes(self.rede), ["T10"])

    def test_tubulacao_inativa_nao_conta_como_caminho_alternativo(self):
        """Uma tubulação inativa não serve de caminho alternativo.

        Cenário: rede de exemplo com D-F (T08) desativada.
        Esperado: ["T01", "T09", "T10"]; E-F (T09) passa a ser ponte.
        Por quê: na rede original, E-F está no ciclo B-D-F-E-B, e é D-F que
        oferece o caminho alternativo. Com D-F inativa, F só se liga ao
        resto da rede por E-F, e retirar E-F isola F e G. Se o algoritmo
        percorresse tubulações inativas, ainda veria esse ciclo e não
        apontaria T09.
        """
        self.rede.alterar_estado("T08", False)

        self.assertEqual(encontrar_pontes(self.rede), ["T01", "T09", "T10"])

    def test_nao_altera_a_rede(self):
        """A busca de pontes não altera a rede recebida.

        Cenário: rede de exemplo com B-D (T04) desativada, para haver
        tubulações nos dois estados.
        Esperado: pontos, tubulações (inclusive o campo ativa) e adjacência
        idênticos antes e depois.
        Por quê: o algoritmo só consulta a rede. A simulação de falhas e a
        interface chamam a busca de pontes sobre redes que continuam em uso
        depois.
        """
        self.rede.alterar_estado("T04", False)
        antes = retrato_da_rede(self.rede)

        encontrar_pontes(self.rede)

        self.assertEqual(retrato_da_rede(self.rede), antes)


class TestPontesCasosGerais(unittest.TestCase):
    """Redes com resposta conhecida: desconexa, ciclo, árvore, linha, ponto."""

    def test_rede_desconexa_encontra_pontes_nas_duas_componentes(self):
        """Em uma rede desconexa, as pontes das duas componentes aparecem.

        Cenário: componente 1 = triângulo A-B-C com a tubulação C-D
        pendurada; componente 2 = linha X-Y-Z. Nenhuma tubulação liga as
        duas. IDs: T01 A-B, T02 B-C, T03 C-A, T04 C-D, T05 X-Y, T06 Y-Z.
        Esperado: ["T04", "T05", "T06"].
        Por quê: as tubulações do triângulo têm caminho alternativo pelo
        próprio triângulo; C-D é a única ligação de D; em uma linha, toda
        tubulação é a única ligação entre os dois lados. Uma busca que
        começasse em A nunca chegaria a X, Y e Z, então o teste garante que
        a busca é reiniciada na segunda componente.
        """
        rede = rede_por_pares("A-B B-C C-A C-D X-Y Y-Z")

        self.assertEqual(encontrar_pontes(rede), ["T04", "T05", "T06"])

    def test_ciclo_nao_tem_pontes(self):
        """Em um ciclo, nenhuma tubulação é ponte.

        Cenário: um triângulo (A-B-C-A) e um quadrado (A-B-C-D-A), testados
        separadamente.
        Esperado: [] nos dois casos.
        Por quê: em um ciclo, os dois extremos de qualquer tubulação
        continuam ligados pelo resto do ciclo, então nenhuma retirada
        isolada separa a rede.
        """
        for texto in ("A-B B-C C-A", "A-B B-C C-D D-A"):
            with self.subTest(rede=texto):
                self.assertEqual(encontrar_pontes(rede_por_pares(texto)), [])

    def test_arvore_todas_as_tubulacoes_sao_pontes(self):
        """Em uma árvore, todas as tubulações são pontes.

        Cenário: árvore em que A se liga a B e C, B se liga a D e E, e C se
        liga a F (5 tubulações, T01 a T05).
        Esperado: ["T01", "T02", "T03", "T04", "T05"].
        Por quê: uma árvore não tem ciclos, então entre dois pontos existe
        um único caminho. Retirar qualquer tubulação separa a árvore em
        duas partes.
        """
        rede = rede_por_pares("A-B A-C B-D B-E C-F")

        self.assertEqual(
            encontrar_pontes(rede), ["T01", "T02", "T03", "T04", "T05"]
        )

    def test_resultado_ordenado_por_id(self):
        """O resultado vem em ordem crescente de ID.

        Cenário: linha A-B-C-D com T01 = A-B, T02 = B-C e T03 = C-D.
        Esperado: ["T01", "T02", "T03"].
        Por quê: as três tubulações são pontes (é uma linha). O Tarjan
        identifica as pontes de baixo para cima na árvore da busca, ou seja,
        T03, T02 e T01, nessa ordem; o teste só passa se a ordenação final
        for de fato aplicada.
        """
        rede = rede_por_pares("A-B B-C C-D")

        self.assertEqual(encontrar_pontes(rede), ["T01", "T02", "T03"])

    def test_ponto_unico_sem_tubulacoes(self):
        """Uma rede com um único ponto e sem tubulações não tem pontes.

        Cenário: rede com o ponto P e nenhuma tubulação.
        Esperado: [].
        Por quê: só tubulações podem ser pontes, e não há nenhuma.
        """
        rede = montar_rede(["P"], [])

        self.assertEqual(encontrar_pontes(rede), [])

    def test_caminho_longo_nao_estoura_recursao(self):
        """Um caminho de 5000 pontos é analisado sem RecursionError.

        Cenário: 5000 pontos em linha (P0000-P0001-...-P4999), ligados por
        4999 tubulações.
        Esperado: as 4999 tubulações são pontes, e nenhuma exceção ocorre.
        Por quê: uma linha é uma árvore, então toda tubulação é ponte. A
        busca em profundidade a partir de P0000 desce 5000 níveis; uma
        versão recursiva passaria do limite de recursão do Python (1000 por
        padrão). A primeira verificação garante que o teste continua
        significativo: se alguém aumentar esse limite acima de 5000, ela
        falha em vez de o teste passar sem provar nada.
        """
        quantidade = 5000
        self.assertGreater(quantidade, sys.getrecursionlimit())

        pontos = [f"P{indice:04d}" for indice in range(quantidade)]
        tubulacoes = [
            (f"T{indice:04d}", pontos[indice], pontos[indice + 1], 1)
            for indice in range(quantidade - 1)
        ]
        rede = montar_rede(pontos, tubulacoes)

        resultado = encontrar_pontes(rede)

        self.assertEqual(len(resultado), quantidade - 1)
        self.assertEqual(resultado, sorted(t[0] for t in tubulacoes))


class TestPontesVerificacaoCruzada(unittest.TestCase):
    """Compara o Tarjan com a força bruta (pontes_por_forca_bruta)."""

    def test_rede_exemplo_original_e_com_cada_falha(self):
        """Tarjan e força bruta concordam na rede de exemplo e nas 10 falhas.

        Cenário: a rede de exemplo original e as 10 variações em que uma
        única tubulação é desativada, cada uma partindo da rede original.
        Esperado: encontrar_pontes == pontes_por_forca_bruta em todas.
        Por quê: a força bruta aplica a definição de ponte diretamente, então
        o resultado dela é o correto por construção. As 11 configurações
        incluem casos em que surgem novas pontes (sem D-F, E-F vira ponte)
        e casos em que a rede já está dividida (sem R-A).
        """
        rede = criar_rede_exemplo()
        with self.subTest(desativada=None):
            self.assertEqual(
                encontrar_pontes(rede), pontes_por_forca_bruta(rede)
            )

        for identificador in rede.tubulacoes:
            cenario = criar_rede_exemplo()
            cenario.alterar_estado(identificador, False)
            with self.subTest(desativada=identificador):
                self.assertEqual(
                    encontrar_pontes(cenario), pontes_por_forca_bruta(cenario)
                )

    def test_redes_pequenas_variadas(self):
        """Tarjan e força bruta concordam em formatos de rede variados.

        Cenário: oito redes pequenas, escritas como pares de pontos, com
        formatos que costumam revelar erros: dois triângulos ligados por
        uma tubulação, ciclo com cauda, dois triângulos com um ponto em
        comum, rede completa, grade, estrela, rede desconexa e dois ciclos
        ligados por uma linha.
        Esperado: encontrar_pontes == pontes_por_forca_bruta em todas.
        Por quê: a força bruta segue a definição de ponte. O caso dos
        triângulos com um ponto em comum é o mais traiçoeiro: C é um ponto
        crítico (retirá-lo separa a rede), mas nenhuma tubulação é ponte.
        """
        redes = {
            "triângulos ligados por C-D": "A-B B-C C-A C-D D-E E-F F-D",
            "ciclo com cauda": "A-B B-C C-D D-A D-E E-F",
            "triângulos com o ponto C em comum": "A-B B-C C-A C-D D-E E-C",
            "completa com 4 pontos": "A-B A-C A-D B-C B-D C-D",
            "grade 3x3": "a-b b-c d-e e-f g-h h-i a-d d-g b-e e-h c-f f-i",
            "estrela": "C-A C-B C-D C-E",
            "desconexa": "A-B B-C C-A D-E E-F X-Y",
            "ciclos ligados por uma linha": "A-B B-C C-A C-D D-E E-F F-G G-E",
        }
        for nome, texto in redes.items():
            rede = rede_por_pares(texto)
            with self.subTest(rede=nome):
                self.assertEqual(
                    encontrar_pontes(rede), pontes_por_forca_bruta(rede)
                )

    def test_redes_aleatorias(self):
        """Tarjan e força bruta concordam em 100 redes aleatórias pequenas.

        Cenário: 100 redes com 1 a 8 pontos, cada par de pontos ligado com
        probabilidade 0,35 e cada tubulação desativada com probabilidade
        0,2. A semente é fixa, então as redes são sempre as mesmas e uma
        falha pode ser reproduzida.
        Esperado: encontrar_pontes == pontes_por_forca_bruta em todas.
        Por quê: a força bruta segue a definição de ponte. As duas últimas
        verificações garantem que o sorteio produziu redes com pontes e
        redes com tubulações ativas que não são pontes, para que a
        comparação não fique restrita a casos triviais.
        """
        gerador = random.Random(2026)
        redes_com_ponte = 0
        redes_com_ativa_que_nao_e_ponte = 0

        for numero in range(100):
            pontos = [f"P{indice}" for indice in range(gerador.randint(1, 8))]
            tubulacoes = []
            for i, origem in enumerate(pontos):
                for destino in pontos[i + 1:]:
                    if gerador.random() < 0.35:
                        identificador = f"T{len(tubulacoes) + 1:02d}"
                        tubulacoes.append((identificador, origem, destino, 1))
            rede = montar_rede(pontos, tubulacoes)
            for identificador in rede.tubulacoes:
                if gerador.random() < 0.2:
                    rede.alterar_estado(identificador, False)

            esperado = pontes_por_forca_bruta(rede)
            with self.subTest(rede=numero):
                self.assertEqual(encontrar_pontes(rede), esperado)

            ativas = sum(1 for t in rede.tubulacoes.values() if t.ativa)
            if esperado:
                redes_com_ponte += 1
            if ativas > len(esperado):
                redes_com_ativa_que_nao_e_ponte += 1

        self.assertGreater(redes_com_ponte, 0)
        self.assertGreater(redes_com_ativa_que_nao_e_ponte, 0)
