from modelos.no import No
from modelos.tubulacao import Tubulacao


class Rede:
    """Organiza a rede em dicionarios de nos, tubulacoes e adjacencia.

    Atributos:
        vertices (dict): identificador do no -> objeto No.
        tubulacoes (dict): identificador da tubulacao -> objeto Tubulacao.
        adjacencia (dict): no -> dicionario {vizinho: id_tubulacao}.
    """

    def __init__(self):
        self.vertices = {}
        self.tubulacoes = {}
        self.adjacencia = {}

    def adicionar_no(self, no):
        """Cadastra um no na rede.

        Parametros:
            no (No): objeto No a ser adicionado.

        Saida:
            None. Levanta ValueError se o identificador ja existir.
        """
        if no.identificador in self.vertices:
            raise ValueError("Ja existe um no com esse identificador.")
        self.vertices[no.identificador] = no
        self.adjacencia[no.identificador] = {}

    def adicionar_tubulacao(self, tubulacao):
        """Cadastra uma tubulacao e registra a conexao nos dois sentidos.

        Parametros:
            tubulacao (Tubulacao): objeto Tubulacao a ser adicionado.

        Saida:
            None. Levanta ValueError em caso de dados invalidos.
        """
        if tubulacao.identificador in self.tubulacoes:
            raise ValueError("Ja existe uma tubulacao com esse identificador.")
        if tubulacao.origem not in self.vertices:
            raise ValueError("O no de origem nao existe.")
        if tubulacao.destino not in self.vertices:
            raise ValueError("O no de destino nao existe.")
        if tubulacao.destino == tubulacao.origem:
            raise ValueError("Origem e destino sao iguais.")
        if tubulacao.distancia <= 0:
            raise ValueError("Distancia invalida.")
        if tubulacao.destino in self.adjacencia[tubulacao.origem]:
            raise ValueError("Ja existe uma tubulacao entre esses nos.")

        self.tubulacoes[tubulacao.identificador] = tubulacao
        self.adjacencia[tubulacao.origem][tubulacao.destino] = tubulacao.identificador
        self.adjacencia[tubulacao.destino][tubulacao.origem] = tubulacao.identificador

    def vizinhos_ativos(self, identificador):
        """Retorna os vizinhos alcançaveis por tubulacoes ativas.

        Parametros:
            identificador (str): ID do no de consulta.

        Saida:
            list[tuple]: lista de pares (vizinho, distancia) para tubulacoes ativas.
        """
        if identificador not in self.vertices:
            raise ValueError("No nao encontrado.")
        vizinhos = []
        for vizinho, id_tubulacao in self.adjacencia[identificador].items():
            tubulacao = self.tubulacoes[id_tubulacao]
            if tubulacao.ativa:
                vizinhos.append((vizinho, tubulacao.distancia))
        return vizinhos

    def alterar_estado(self, identificador, ativa):
        """Altera o estado (ativo/inativo) de uma tubulacao.

        Parametros:
            identificador (str): ID da tubulacao.
            ativa (bool): novo estado da tubulacao.

        Saida:
            None. Levanta ValueError se a tubulacao nao existir.
        """
        if identificador not in self.tubulacoes:
            raise ValueError("Tubulacao nao encontrada.")
        self.tubulacoes[identificador].ativa = ativa

    def copiar(self):
        """Cria uma copia independente da rede, com novos objetos.

        Saida:
            Rede: copia da rede, nao ligada ao objeto original.
        """
        copia = Rede()
        for no in self.vertices.values():
            copia.adicionar_no(No(no.identificador, no.nome, no.tipo))
        for tubulacao in self.tubulacoes.values():
            copia.adicionar_tubulacao(
                Tubulacao(
                    tubulacao.identificador,
                    tubulacao.origem,
                    tubulacao.destino,
                    tubulacao.distancia,
                    tubulacao.ativa,
                )
            )
        return copia
