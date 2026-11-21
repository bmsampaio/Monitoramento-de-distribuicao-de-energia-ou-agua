"""Carrega os CSVs de nós e tubulações em uma Rede.

Formato (UTF-8, vírgula como separador, ponto como separador decimal):
    nos.csv:        id,nome,tipo
    tubulacoes.csv: id,origem,destino,distancia_km,ativa

Dados inválidos levantam ValueError com o arquivo e a linha do problema.
"""

import csv
import math

from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao

COLUNAS_NOS = ("id", "nome", "tipo")
COLUNAS_TUBULACOES = ("id", "origem", "destino", "distancia_km", "ativa")


def _ler_linhas(caminho_csv, colunas):
    """Confere o cabeçalho e devolve (local, campos) de cada linha.

    local é "arquivo, linha N", para as mensagens de erro. Os campos vêm sem
    espaços nas pontas, e campos vazios são rejeitados.
    """
    # utf-8-sig aceita arquivos salvos pelo Excel, que começam com BOM.
    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        faltando = [c for c in colunas if c not in (leitor.fieldnames or [])]
        if faltando:
            raise ValueError(
                f"{caminho_csv}: faltam as colunas {', '.join(faltando)}."
            )

        linhas = []
        for linha in leitor:
            local = f"{caminho_csv}, linha {leitor.line_num}"
            campos = {c: (linha[c] or "").strip() for c in colunas}
            vazios = [c for c in colunas if not campos[c]]
            if vazios:
                raise ValueError(f"{local}: campo vazio em {', '.join(vazios)}.")
            linhas.append((local, campos))
    return linhas


def carregar_nos(rede, caminho_csv):
    """Cadastra na rede os nós de caminho_csv.

    Raises:
        ValueError: cabeçalho incompleto, campo vazio ou ID repetido.
    """
    for local, campos in _ler_linhas(caminho_csv, COLUNAS_NOS):
        try:
            rede.adicionar_no(No(campos["id"], campos["nome"], campos["tipo"]))
        except ValueError as erro:
            raise ValueError(f"{local}: {erro}") from None


def carregar_tubulacoes(rede, caminho_csv):
    """Cadastra na rede as tubulações de caminho_csv. Os nós devem vir antes.

    Raises:
        ValueError: cabeçalho incompleto, campo vazio, distância não numérica
        ou <= 0, estado diferente de true/false, nó inexistente ou conexão
        repetida.
    """
    for local, campos in _ler_linhas(caminho_csv, COLUNAS_TUBULACOES):
        try:
            distancia = float(campos["distancia_km"])
        except ValueError:
            distancia = math.nan
        if not math.isfinite(distancia):
            raise ValueError(
                f"{local}: distância inválida {campos['distancia_km']!r}."
            )

        # bool("false") é True, por isso a comparação com o texto.
        estado = campos["ativa"].lower()
        if estado not in ("true", "false"):
            raise ValueError(
                f"{local}: estado inválido {campos['ativa']!r}; use true ou false."
            )

        tubulacao = Tubulacao(
            identificador=campos["id"],
            origem=campos["origem"],
            destino=campos["destino"],
            distancia=distancia,
            ativa=(estado == "true"),
        )
        try:
            rede.adicionar_tubulacao(tubulacao)
        except ValueError as erro:
            raise ValueError(f"{local}: {erro}") from None


def carregar_rede(caminho_nos, caminho_tubulacoes):
    """Monta uma Rede nova a partir dos dois CSVs.

    Returns:
        Rede: rede com os nós e as tubulações dos arquivos.

    Raises:
        ValueError: qualquer dado inválido, com o arquivo e a linha.
    """
    rede = Rede()
    carregar_nos(rede, caminho_nos)
    carregar_tubulacoes(rede, caminho_tubulacoes)
    return rede
