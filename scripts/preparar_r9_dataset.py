import csv
from pathlib import Path

from openpyxl import load_workbook


PASTA_PROJETO = Path(__file__).resolve().parent.parent
PASTA_DADOS = PASTA_PROJETO / "dados"
ARQUIVO_EXCEL = (
    PASTA_DADOS
    / "originais"
    / "R9_water_distribution_network_input_data.xlsx"
)

def salvar_csv(caminho, colunas, linhas):
    with caminho.open("w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(colunas)
        escritor.writerows(linhas)

def preparar_dados():
    planilha = load_workbook(ARQUIVO_EXCEL, data_only=True)

    nos = [["R", "Reservatório", "reservatorio"]]
    tubulacoes = []

    try:
        aba = planilha["DATOS"]

        # ignorar o cabeçalho.
        for linha in aba.iter_rows(min_row=2, values_only=True):
            id_tubulacao, comprimento_m, origem, destino = linha[:4]
            id_no = linha[4]

            if id_tubulacao is not None:
                # O reservatório aparece como "-" na planilha.
                if origem == "-":
                    origem = "R"
                else:
                    origem = str(int(origem))

                tubulacoes.append([
                    f"T{int(id_tubulacao)}",
                    origem,
                    str(int(destino)),
                    float(comprimento_m) / 1000,
                    "true",
                ])

            # A tabela de nós é independente da tabela de tubulações.
            if id_no is not None:
                id_no = str(int(id_no))

                nos.append([
                    id_no,
                    f"Ponto de demanda {id_no}",
                    "ponto_demanda",
                ])
    finally:
        planilha.close()

    salvar_csv(
        PASTA_DADOS / "nos.csv",
        ["id", "nome", "tipo"],
        nos,
    )

    salvar_csv(
        PASTA_DADOS / "tubulacoes.csv",
        ["id", "origem", "destino", "distancia_km", "ativa"],
        tubulacoes,
    )

    print(f"nos.csv criado com {len(nos)} nós.")
    print(f"tubulacoes.csv criado com {len(tubulacoes)} tubulações.")

preparar_dados()