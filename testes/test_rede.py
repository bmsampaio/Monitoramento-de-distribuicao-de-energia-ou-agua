from modelos.no import No
from modelos.rede import Rede
from modelos.tubulacao import Tubulacao
from servicos.leitura_csv import carregar_nos, carregar_tubulacoes, carregar_rede

rede = Rede()
rede.adicionar_no(No("R", "Reservatório", "reservatorio"))

assert "R" in rede.vertices
assert rede.adjacencia["R"] == {}

print("Teste de cadastro do reservatório passou!")

rede.adicionar_no(No("1", "Ponto de demanda 1", "ponto_demanda"))
rede.adicionar_tubulacao(Tubulacao("T1", "R", "1", 2.54))

assert rede.adjacencia["R"]["1"] == "T1"
assert rede.adjacencia["1"]["R"] == "T1"
assert len(rede.tubulacoes) == 1

print("Teste de conexão nos dois sentidos passou!")

assert rede.vizinhos_ativos("R") == [("1", 2.54)]

rede.alterar_estado("T1", False)

assert "T1" in rede.tubulacoes
assert rede.vizinhos_ativos("R") == []
assert rede.vizinhos_ativos("1") == []

print("Teste de desativação da tubulação passou!")

rede.alterar_estado("T1", True)

assert rede.vizinhos_ativos("R") == [("1", 2.54)]
assert rede.vizinhos_ativos("1") == [("R", 2.54)]
assert len(rede.tubulacoes) == 1

print("Teste de reativação da tubulação passou!")

rede_com_falha = rede.copiar()
rede_com_falha.alterar_estado("T1", False)

assert rede_com_falha.vizinhos_ativos("R") == []
assert rede.vizinhos_ativos("R") == [("1", 2.54)]

print("Teste de independência da cópia passou!")

rede_r9 = Rede()
carregar_nos(rede_r9, "dados/nos.csv")

assert len(rede_r9.vertices) == 62
assert rede_r9.vertices["R"].nome == "Reservatório"
assert rede_r9.adjacencia["R"] == {}

print("Teste de leitura dos nós da R-9 passou!")

carregar_tubulacoes(rede_r9, "dados/tubulacoes.csv")

assert len(rede_r9.tubulacoes) == 72
assert rede_r9.adjacencia["R"]["1"] == "T1"
assert rede_r9.adjacencia["1"]["R"] == "T1"
assert ("1", 2.54) in rede_r9.vizinhos_ativos("R")

print("Teste de leitura das tubulações da R-9 passou!")

rede_completa = carregar_rede("dados/nos.csv", "dados/tubulacoes.csv")

assert len(rede_completa.vertices) == 62
assert len(rede_completa.tubulacoes) == 72
assert ("1", 2.54) in rede_completa.vizinhos_ativos("R")

print("Teste de carregamento completo da R-9 passou!")

rede_teste = Rede()
rede_teste.adicionar_no(No("R", "Reservatório", "reservatorio"))

try:
    rede_teste.adicionar_tubulacao(Tubulacao("T1", "R", "X", 2.54))
except ValueError as erro:
    assert str(erro) == "O nó de destino não existe."
else:
    raise AssertionError("A rede aceitou uma tubulação com destino inexistente.")

assert rede_teste.tubulacoes == {}
assert rede_teste.adjacencia["R"] == {}

print("Teste de rejeição de destino inexistente passou!")

rede_teste.adicionar_no(No("1", "Ponto de demanda 1", "ponto_demanda"))
rede_teste.adicionar_tubulacao(Tubulacao("T1", "R", "1", 2.54))

try:
    rede_teste.adicionar_tubulacao(Tubulacao("T2", "1", "R", 2.54))
except ValueError as erro:
    assert str(erro) == "Já existe uma tubulação entre esses nós."
else:
    raise AssertionError("A rede aceitou uma segunda tubulação entre os mesmos nós.")

assert len(rede_teste.tubulacoes) == 1
assert rede_teste.adjacencia["R"]["1"] == "T1"
assert rede_teste.adjacencia["1"]["R"] == "T1"

print("Teste de rejeição de conexão duplicada passou!")