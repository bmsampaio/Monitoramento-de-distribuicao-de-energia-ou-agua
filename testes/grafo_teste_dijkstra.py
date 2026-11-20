
from copy import deepcopy


class RedeTeste:
    """Grafo não direcionado com tubulações que podem ser desativadas."""

    def __init__(self):
        self.vertices = set()
        self.tubulacoes = {}

    def adicionar_no(self, identificador):
        self.vertices.add(identificador)

    def adicionar_tubulacao(self, origem, destino, distancia):
        if origem not in self.vertices or destino not in self.vertices:
            raise ValueError("Os dois vértices devem existir")
        if origem == destino or distancia <= 0:
            raise ValueError("Tubulação inválida")

        identificador = f"{origem}-{destino}"
        if any(
            {t["origem"], t["destino"]} == {origem, destino}
            for t in self.tubulacoes.values()
        ):
            raise ValueError("Já existe uma tubulação entre esses pontos")

        self.tubulacoes[identificador] = {
            "origem": origem,
            "destino": destino,
            "distancia": distancia,
            "ativa": True,
        }

    def vizinhos_ativos(self, vertice):
        """Retorna pares (vizinho, distância), ignorando tubulações inativas."""
        if vertice not in self.vertices:
            raise ValueError(f"Vértice inexistente: {vertice}")

        vizinhos = []
        for tubulacao in self.tubulacoes.values():
            if not tubulacao["ativa"]:
                continue
            if tubulacao["origem"] == vertice:
                vizinhos.append((tubulacao["destino"], tubulacao["distancia"]))
            elif tubulacao["destino"] == vertice:
                vizinhos.append((tubulacao["origem"], tubulacao["distancia"]))
        return vizinhos

    def alterar_estado(self, identificador, ativo):
        if identificador not in self.tubulacoes:
            raise ValueError(f"Tubulação inexistente: {identificador}")
        self.tubulacoes[identificador]["ativa"] = bool(ativo)

    def copiar(self):
        return deepcopy(self)


def criar_rede_exemplo():
    """Cria exatamente os 8 vértices e 10 tubulações do plano do grupo."""
    rede = RedeTeste()
    for vertice in "RABCDEFG":
        rede.adicionar_no(vertice)

    conexoes = [
        ("R", "A", 2),
        ("A", "B", 2),
        ("A", "C", 3),
        ("B", "D", 2),
        ("B", "E", 5),
        ("C", "D", 6),
        ("C", "E", 4),
        ("D", "F", 2),
        ("E", "F", 3),
        ("F", "G", 2),
    ]
    for origem, destino, distancia in conexoes:
        rede.adicionar_tubulacao(origem, destino, distancia)
    return rede


def executar_testes():
    # O arquivo algoritmos/dijkstra.py deve conter a função dijkstra(rede, origem, destino).
    from algoritmos.dijkstra import dijkstra

    original = criar_rede_exemplo()

    caminho, distancia = dijkstra(original, "R", "G")
    assert caminho == ["R", "A", "B", "D", "F", "G"]
    assert distancia == 10
    print("[OK] Rede original: caminho de 10 km")

    sem_bd = original.copiar()
    sem_bd.alterar_estado("B-D", False)
    caminho, distancia = dijkstra(sem_bd, "R", "G")
    rotas_validas = [
        ["R", "A", "B", "E", "F", "G"],
        ["R", "A", "C", "E", "F", "G"],
    ]
    assert caminho in rotas_validas and distancia == 14
    print("[OK] Falha B-D: caminho alternativo de 14 km")

    sem_ra = original.copiar()
    sem_ra.alterar_estado("R-A", False)
    assert dijkstra(sem_ra, "R", "G") == ([], None)
    print("[OK] Falha R-A: destino inacessível")

    sem_fg = original.copiar()
    sem_fg.alterar_estado("F-G", False)
    assert dijkstra(sem_fg, "R", "G") == ([], None)
    print("[OK] Falha F-G: destino inacessível")

    assert dijkstra(original, "R", "R") == (["R"], 0)
    assert original.tubulacoes["B-D"]["ativa"]
    print("[OK] Origem igual ao destino e rede original preservada")


if __name__ == "__main__":
    executar_testes()
