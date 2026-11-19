from modelos.no import No
from modelos.tubulacao import Tubulacao

class Rede:
    def __init__(self):
        self.vertices = {}
        self.tubulacoes = {}
        self.adjacencia = {}

    def adicionar_no(self, no):
        if no.identificador in self.vertices:
            raise ValueError("Já existe um nó com esse identificador.")

        self.vertices[no.identificador] = no
        self.adjacencia[no.identificador] = {}

    def adicionar_tubulacao(self, tubulacao):
        if tubulacao.identificador in self.tubulacoes:
            raise ValueError("Já existe uma tubulação com esse identificador.")

        if tubulacao.origem not in self.vertices:
            raise ValueError("O nó de origem não existe.")
        
        if tubulacao.destino not in self.vertices:
            raise ValueError("O nó de destino não existe.")
        
        if tubulacao.destino == tubulacao.origem:
            raise ValueError("Os nós de destino e origem são iguais.")

        if tubulacao.distancia <= 0:
            raise ValueError("Distância inválida")
       
        if tubulacao.destino in self.adjacencia[tubulacao.origem]:
            raise ValueError("Já existe uma tubulação entre esses nós.")
        
        self.tubulacoes[tubulacao.identificador] = tubulacao
        self.adjacencia[tubulacao.origem][tubulacao.destino] = tubulacao.identificador
        self.adjacencia[tubulacao.destino][tubulacao.origem] = tubulacao.identificador

    def vizinhos_ativos(self, identificador):
        if identificador not in self.vertices:
            raise ValueError("Nó não encontrado")
        
        vizinhos = []
        for vizinho, id_tubulacao in self.adjacencia[identificador].items():
            tubulacao = self.tubulacoes[id_tubulacao]
            
            if tubulacao.ativa:
                vizinhos.append((vizinho, tubulacao.distancia))
                
        return vizinhos

    def alterar_estado(self, identificador, ativa):
        if identificador not in self.tubulacoes:
            raise ValueError("Tubulação não encontrada")
        
        tubulacao = self.tubulacoes[identificador]
        tubulacao.ativa = ativa

    def copiar(self):
        copia = Rede()
        
        for no in self.vertices.values():
            novo_no = No(no.identificador, no.nome, no.tipo)
            copia.adicionar_no(novo_no)
            
        for tubulacao in self.tubulacoes.values():
            nova_tubulacao = Tubulacao(
                tubulacao.identificador,
                tubulacao.origem,
                tubulacao.destino,
                tubulacao.distancia,
                tubulacao.ativa
            )
            copia.adicionar_tubulacao(nova_tubulacao)

        return copia
