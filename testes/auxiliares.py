"""Funções de apoio compartilhadas pelos testes de BFS e de pontes.

Os testes montam as próprias redes, sem depender de exemplos/rede_exemplo.py
nem dos CSVs, que são mantidos por outras pessoas do grupo. Assim, uma
mudança nesses arquivos não quebra os testes dos algoritmos.
"""

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao


def montar_rede(pontos, tubulacoes):
    """Monta uma Rede com os pontos e as tubulações informados, todos ativos.

    Args:
        pontos (list[str]): IDs dos pontos, na ordem de cadastro.
        tubulacoes (list[tuple]): tuplas (id, origem, destino, distancia),
            na ordem de cadastro. Para desativar uma tubulação, usar
            rede.alterar_estado(id, False) depois de montar a rede.

    Returns:
        Rede: rede nova, independente de qualquer outra.
    """
    rede = Rede()
    for ponto in pontos:
        rede.adicionar_no(No(ponto, f"Ponto {ponto}", "ponto_demanda"))
    for identificador, origem, destino, distancia in tubulacoes:
        rede.adicionar_tubulacao(
            Tubulacao(identificador, origem, destino, distancia)
        )
    return rede


def rede_por_pares(texto):
    """Monta uma rede a partir de um texto como "A-B B-C C-A".

    Serve para escrever redes de teste pequenas em uma linha. Cada par
    "X-Y" vira uma tubulação ativa de 1 km entre X e Y, com IDs T01, T02,
    ... na ordem em que os pares aparecem no texto. Os pontos são
    cadastrados na ordem em que aparecem pela primeira vez. A distância é
    sempre 1 porque BFS e pontes não usam distâncias.

    Args:
        texto (str): pares separados por espaço; cada par tem os IDs dos
            dois pontos separados por hífen.

    Returns:
        Rede: rede nova com os pontos e tubulações descritos.

    Exemplo:
        rede_por_pares("A-B B-C") cria os pontos A, B e C e as tubulações
        T01 (A-B) e T02 (B-C).
    """
    pares = [par.split("-") for par in texto.split()]
    pontos = []
    for par in pares:
        for ponto in par:
            if ponto not in pontos:
                pontos.append(ponto)
    tubulacoes = [
        (f"T{indice:02d}", origem, destino, 1)
        for indice, (origem, destino) in enumerate(pares, start=1)
    ]
    return montar_rede(pontos, tubulacoes)


def criar_rede_exemplo():
    """Monta a rede de exemplo do projeto: 8 pontos e 10 tubulações ativas.

    É a rede descrita no README, seção 7 ("Dados e rede inicial"); em
    versões mais novas do README ela está na seção 8 ("Rede pequena para
    testes"). Os resultados esperados que os testes conferem também vêm do
    README.

    Os IDs seguem a ordem das conexões no README:

        T01 R-A 2 km    T06 C-D 6 km
        T02 A-B 2 km    T07 C-E 4 km
        T03 A-C 3 km    T08 D-F 2 km
        T04 B-D 2 km    T09 E-F 3 km
        T05 B-E 5 km    T10 F-G 2 km

    R só tem a tubulação R-A, e G só tem F-G. Entre A e F há vários
    caminhos (por B ou por C, passando por D ou por E), que formam ciclos.

    Returns:
        Rede: rede nova a cada chamada, para que as falhas simuladas em um
        teste não afetem os outros.
    """
    rede = Rede()
    rede.adicionar_no(No("R", "Reservatório principal", "reservatorio"))
    rede.adicionar_no(No("A", "Estação de bombeamento", "bombeamento"))
    rede.adicionar_no(No("B", "Ponto intermediário B", "intermediario"))
    rede.adicionar_no(No("C", "Ponto intermediário C", "intermediario"))
    for setor in "DEFG":
        rede.adicionar_no(No(setor, f"Setor {setor}", "setor"))

    conexoes = [
        ("R", "A", 2), ("A", "B", 2), ("A", "C", 3), ("B", "D", 2),
        ("B", "E", 5), ("C", "D", 6), ("C", "E", 4), ("D", "F", 2),
        ("E", "F", 3), ("F", "G", 2),
    ]
    for indice, (origem, destino, distancia) in enumerate(conexoes, start=1):
        rede.adicionar_tubulacao(
            Tubulacao(f"T{indice:02d}", origem, destino, distancia)
        )
    return rede


def retrato_da_rede(rede):
    """Resume todo o estado da rede em uma estrutura comparável com ==.

    Usado nos testes que verificam que um algoritmo não altera a rede: tira-se
    um retrato antes e outro depois de chamar o algoritmo e compara-se os
    dois. Inclui os pontos, todos os campos de cada tubulação (inclusive
    ativa) e a adjacência.

    Args:
        rede (Rede): rede a ser resumida. Não é alterada.

    Returns:
        tuple: (pontos, tubulacoes, adjacencia), em que pontos mapeia ID para
        (nome, tipo), tubulacoes mapeia ID para (origem, destino, distancia,
        ativa) e adjacencia é uma cópia de rede.adjacencia.
    """
    pontos = {
        identificador: (no.nome, no.tipo)
        for identificador, no in rede.vertices.items()
    }
    tubulacoes = {
        identificador: (t.origem, t.destino, t.distancia, t.ativa)
        for identificador, t in rede.tubulacoes.items()
    }
    adjacencia = {
        ponto: dict(vizinhos) for ponto, vizinhos in rede.adjacencia.items()
    }
    return pontos, tubulacoes, adjacencia
