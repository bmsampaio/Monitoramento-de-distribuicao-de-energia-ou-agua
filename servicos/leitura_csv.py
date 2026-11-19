from modelos.tubulacao import Tubulacao
from modelos.rede import Rede
import csv

from modelos.no import No


def carregar_nos(rede, caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            no = No(linha["id"], linha["nome"], linha["tipo"])
            rede.adicionar_no(no)
            
def carregar_tubulacoes(rede, caminho_csv):
    with open(caminho_csv, encoding="utf-8", newline="") as arquivo:
        for linha in csv.DictReader(arquivo):
            estado = linha["ativa"].strip().lower()
            if estado not in ("true", "false"):
                raise ValueError(f"Estado inválido na tubulação {linha['id']}: {estado!r}")

            tubulacao = Tubulacao(
                identificador=linha["id"],
                origem=linha["origem"],
                destino=linha["destino"],
                distancia=float(linha["distancia_km"]),
                ativa=(estado == "true"),
            )
            rede.adicionar_tubulacao(tubulacao)

def carregar_rede(caminho_nos, caminho_tubulacoes):
    rede = Rede()
    carregar_nos(rede, caminho_nos)
    carregar_tubulacoes(rede, caminho_tubulacoes)
    return rede