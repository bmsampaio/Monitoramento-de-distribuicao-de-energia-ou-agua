# Combinados do grupo

Contratos das funções compartilhadas entre os módulos. Cada responsável registra a sua parte. Para mudar nome, argumentos ou retorno de uma função daqui, avisar antes quem a usa.

## BFS e pontes (integrante 2 - Thiago)

Valem para as duas funções:

- Consideram só tubulações ativas.
- Não alteram a rede recebida. Para simular uma falha, desativar a tubulação em `rede.copiar()` e passar a cópia.
- Os exemplos usam a rede de exemplo de `testes/auxiliares.py`, com IDs na ordem do README: `T01` = R-A, `T02` = A-B, ..., `T08` = D-F, `T09` = E-F, `T10` = F-G.

### `bfs(rede, origem)`

Arquivo `algoritmos/bfs.py`. Importação: `from algoritmos.bfs import bfs`.

| | |
|---|---|
| Recebe | `rede` (`Rede`) e `origem` (`str`, ID de um ponto, ex.: `"R"`) |
| Devolve | `list[str]` com os IDs alcançáveis a partir da origem por tubulações ativas |
| Erro | `ValueError` se `origem` não existe na rede |
| Complexidade | O(V + E) |

Detalhes:

- A origem vem sempre em primeiro lugar, então a lista nunca é vazia.
- Sem repetição, na ordem de visita: primeiro os pontos a 1 tubulação da origem, depois os a 2, e assim por diante. Dentro de uma camada, segue a ordem de cadastro dos pontos.
- As distâncias são ignoradas. O menor caminho é papel do Dijkstra.
- Ponto existente sem ligações devolve só ele: `["P"]`. Ponto inexistente levanta `ValueError("O ponto de origem 'Z' não existe na rede.")`.

```python
bfs(rede, "R")   # ['R', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

copia = rede.copiar()
copia.alterar_estado("T01", False)   # desativa R-A
bfs(copia, "R")  # ['R']
```

Pontos que ficaram inacessíveis por causa de uma falha (subtrair duas listas com `-` dá `TypeError`):

```python
depois = set(bfs(copia, "R"))
inacessiveis = [p for p in bfs(rede, "R") if p not in depois]  # mantém a ordem de visita
```

### `encontrar_pontes(rede)`

Arquivo `algoritmos/pontes.py`. Importação: `from algoritmos.pontes import encontrar_pontes`.

| | |
|---|---|
| Recebe | `rede` (`Rede`) |
| Devolve | `list[str]` com os IDs das tubulações ativas que são pontes |
| Erro | Nenhuma exceção própria. Sem pontes, devolve `[]` |
| Complexidade | O(V + E + P log P), P = número de pontes |

Detalhes:

- Ordenada com `sorted()`, ou seja, ordem de texto. Com IDs sem zeros à esquerda, como na R-9, `"T10"` vem antes de `"T2"`.
- Tubulação inativa nunca aparece no resultado.
- Analisa todas as componentes, inclusive quando a rede já está dividida.
- Os extremos de uma ponte, para desenhá-la, estão em `rede.tubulacoes[id].origem` e `rede.tubulacoes[id].destino`.
- Uma falha pode criar pontes novas. Recalcular na rede com a falha, sem reaproveitar a lista da rede original.

```python
encontrar_pontes(rede)   # ['T01', 'T10'] (R-A e F-G)

copia = rede.copiar()
copia.alterar_estado("T08", False)   # desativa D-F
encontrar_pontes(copia)  # ['T01', 'T09', 'T10'] (E-F vira ponte)
```

Na rede R-9, o resultado é `['T1', 'T8']`.

### O que as duas funções usam da `Rede`

Se algum destes itens mudar, as funções precisam ser ajustadas.

| Item | Formato esperado | Usado por |
|---|---|---|
| `rede.vertices` | dicionário indexado pelo ID do ponto | `bfs` (valida a origem) e `encontrar_pontes` (percorre os pontos) |
| `rede.vizinhos_ativos(id)` | lista de pares `(vizinho, distancia)` | as duas |
| `rede.adjacencia[u][v]` | ID da tubulação entre `u` e `v` | `encontrar_pontes` |

### Pendente: lista ou conjunto

O README do `main` propõe que as duas funções devolvam um conjunto. O código devolve lista, para manter a ordem de visita da BFS e um resultado previsível nas pontes. Quem precisar de operações de conjunto converte com `set(...)`. A confirmar com o grupo.
