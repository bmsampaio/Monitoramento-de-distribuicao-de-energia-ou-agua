# Explicação do código

Este documento explica o que cada parte do código faz e como as partes se conectam. Para instalar e executar, ver o [README](../README.md). Argumentos, retornos e erros de cada função compartilhada estão em [combinados.md](combinados.md).

Os exemplos usam a rede pequena do plano (8 pontos, 10 tubulações), descrita na seção 3.3.

## 1. Visão geral

A rede de distribuição de água é representada como um **grafo não direcionado e ponderado**:

- cada ponto da rede (reservatório, estação de bombeamento, setor) é um vértice;
- cada tubulação é uma aresta;
- o peso de uma aresta é a distância da tubulação em km;
- cada tubulação está ativa ou inativa. **Uma falha é uma tubulação desativada**, e várias podem falhar ao mesmo tempo.

### 1.1 Camadas

```text
app.py ............................ interface (Streamlit)
  |-- visualizacao.py ............. desenho da rede (Matplotlib)
  |
  `-- servicos/simulacao.py ....... compara a rede antes e depois das falhas
        |-- algoritmos/bfs.py ....... quem está ligado à origem
        |-- algoritmos/dijkstra.py .. menor caminho em km
        `-- algoritmos/pontes.py .... tubulações críticas (Tarjan)
              |
              `-- modelos/ ........ No, Tubulacao e Rede (o grafo)

De onde vem a rede:
  planilha R-9 -> scripts/preparar_r9_dataset.py -> dados/*.csv -> servicos/leitura_csv.py -> Rede
  exemplos/rede_exemplo.py -> Rede (rede pequena do plano)
```

Cada camada só usa as de baixo. Os algoritmos não sabem que existe interface, e a interface não chama os algoritmos diretamente: tudo passa pela simulação.

### 1.2 O que acontece ao clicar em "Simular falhas"

1. O usuário escolhe uma ou mais tubulações na lista e clica no botão. O botão copia a seleção para `st.session_state.falhas`, e o Streamlit roda o `app.py` de novo, de cima a baixo (é assim a cada interação).
2. O `app.py` chama `simular_falhas(rede, origem, destino, falhas)`.
3. A simulação calcula BFS, Dijkstra e pontes na rede original.
4. Faz uma cópia da rede, desativa **todas** as tubulações escolhidas **na cópia** e calcula tudo de novo.
5. Compara os dois cenários: pontos que perderam a ligação, mudança de rota e distância, pontes novas.
6. O `app.py` mostra as métricas e desenha a rede duas vezes, antes e depois, em uma página com zoom (seção 6.3).

"Restaurar rede" só esvazia `falhas` e a seleção. Como a rede original nunca é alterada, não há nada a desfazer: a execução seguinte já mostra a rede sem falha.

### 1.3 Quem fez cada parte

| Parte | Arquivos | Integrante |
|---|---|---|
| Modelos e dados | `modelos/`, `servicos/leitura_csv.py`, `scripts/`, `dados/` | 1 - Bárbara |
| BFS e pontes | `algoritmos/bfs.py`, `algoritmos/pontes.py` | 2 - Thiago |
| Dijkstra e desempenho | `algoritmos/dijkstra.py`, `desempenho/` | 3 - Felipe |
| Interface | `app.py`, `visualizacao.py` | 4 |
| Simulação e integração | `servicos/simulacao.py` | 5 - João Victor |

## 2. Modelos (`modelos/`)

### 2.1 `No` e `Tubulacao`

São classes só de dados, sem métodos.

```python
No("R", "Reservatório principal", "reservatorio")
Tubulacao("T01", "R", "A", 2)          # ativa=True por padrão
```

| Classe | Atributos |
|---|---|
| `No` | `identificador`, `nome`, `tipo` |
| `Tubulacao` | `identificador`, `origem`, `destino`, `distancia` (km), `ativa` |

`origem` e `destino` só dão nome às duas pontas. O grafo não tem sentido: a água pode ir de `origem` para `destino` ou o contrário.

### 2.2 `Rede`

A rede guarda três dicionários:

| Atributo | Chave | Valor |
|---|---|---|
| `vertices` | ID do ponto | objeto `No` |
| `tubulacoes` | ID da tubulação | objeto `Tubulacao` |
| `adjacencia` | ID do ponto | `{vizinho: ID da tubulação}` |

`adjacencia` é a **lista de adjacência**. Cada tubulação aparece nos dois sentidos. Na rede de exemplo:

```python
rede.adjacencia["R"]  # {"A": "T01"}
rede.adjacencia["A"]  # {"R": "T01", "B": "T02", "C": "T03"}
```

A adjacência guarda o **ID** da tubulação, não a distância nem o estado. Assim, desativar uma tubulação é só mudar o campo `ativa` do objeto; a adjacência continua igual e a falha pode ser desfeita.

| Método | O que faz | Custo |
|---|---|---|
| `adicionar_no(no)` | Valida o ID e cria uma entrada vazia na adjacência | O(1) |
| `adicionar_tubulacao(t)` | Valida e registra a tubulação nos dois sentidos | O(1) |
| `vizinhos_ativos(id)` | Lista de `(vizinho, distancia)` só das tubulações ativas | O(grau do ponto) |
| `alterar_estado(id, ativa)` | Ativa ou desativa uma tubulação | O(1) |
| `copiar()` | Cria uma rede nova, com objetos `No` e `Tubulacao` novos | O(V + E) |

Validações (todas lançam `ValueError`):

- ID de ponto ou de tubulação repetido;
- origem ou destino que não existe;
- laço (origem igual ao destino);
- distância menor ou igual a zero;
- segunda tubulação entre o mesmo par. Como a conexão é registrada nos dois sentidos, a checagem `destino in adjacencia[origem]` também pega o par invertido (B-A depois de A-B);
- ponto inexistente em `vizinhos_ativos` e tubulação inexistente em `alterar_estado`.

Pontos importantes:

- **`vizinhos_ativos` é o único ponto de contato dos algoritmos com a rede.** É nele que as tubulações inativas são descartadas, então nenhum algoritmo precisa se preocupar com isso.
- **`copiar()` cria objetos novos** passando pelos próprios métodos de cadastro. Por isso desativar uma tubulação na cópia não muda a original. A simulação depende disso.
- Dicionários do Python mantêm a ordem de inserção, então os vizinhos saem na ordem de cadastro. Isso deixa a BFS e o Tarjan determinísticos: a mesma rede dá sempre o mesmo resultado.

## 3. Dados

### 3.1 Preparação da R-9 (`scripts/preparar_r9_dataset.py`)

Converte a planilha original (`dados/originais/R9_water_distribution_network_input_data.xlsx`) nos dois CSVs usados pelo programa. Roda uma vez, separado da aplicação.

- Lê a aba `DATOS` com `openpyxl`. As quatro primeiras colunas descrevem a tubulação (ID, comprimento em metros, ponto inicial, ponto final), e a quinta lista os IDs dos pontos. São duas tabelas independentes na mesma aba.
- O reservatório aparece como `-` na planilha e vira `"R"`.
- Os IDs viram texto, as tubulações ganham o prefixo `"T"` e o comprimento é dividido por 1000 (metros para km).
- Todas as tubulações começam ativas.
- Gera `dados/nos.csv` (62 pontos) e `dados/tubulacoes.csv` (72 tubulações).

### 3.2 Leitura dos CSVs (`servicos/leitura_csv.py`)

Transforma os CSVs em uma `Rede`.

| Função | O que faz |
|---|---|
| `_ler_linhas(caminho, colunas)` | Abre o arquivo, confere o cabeçalho, tira espaços das pontas e rejeita campo vazio. Devolve pares `(local, campos)`, em que `local` é `"arquivo, linha N"` |
| `carregar_nos(rede, caminho)` | Cria um `No` por linha |
| `carregar_tubulacoes(rede, caminho)` | Converte distância e estado e cria uma `Tubulacao` por linha |
| `carregar_rede(caminho_nos, caminho_tubulacoes)` | Cria a `Rede` e carrega os nós antes das tubulações |

Detalhes:

- O arquivo é aberto como `utf-8-sig`, que aceita CSVs salvos pelo Excel (começam com um caractere invisível, o BOM).
- A distância passa por `float()`. Texto, `nan` e `inf` são rejeitados aqui; distância <= 0 é rejeitada pela `Rede`.
- O estado só aceita `true` ou `false`, sem diferenciar maiúsculas. Não se usa `bool(texto)`, porque `bool("false")` é `True` (qualquer texto não vazio é verdadeiro).
- Os nós vêm primeiro porque uma tubulação só pode ser cadastrada se os dois pontos já existirem.
- Erros da própria `Rede` (nó inexistente, conexão repetida) são relançados com o local, por exemplo:
  `dados/tubulacoes.csv, linha 3: O nó de destino não existe.`

### 3.3 Rede de exemplo (`exemplos/rede_exemplo.py`)

A rede pequena do plano, fácil de conferir à mão. É usada pela interface e pelos testes.

R é o reservatório, A a estação de bombeamento, B e C pontos intermediários, e D, E, F e G setores.

| ID | Conexão | km | | ID | Conexão | km |
|---|---|---|---|---|---|---|
| T01 | R-A | 2 | | T06 | C-D | 6 |
| T02 | A-B | 2 | | T07 | C-E | 4 |
| T03 | A-C | 3 | | T08 | D-F | 2 |
| T04 | B-D | 2 | | T09 | E-F | 3 |
| T05 | B-E | 5 | | T10 | F-G | 2 |

R só se liga à rede por R-A, e G só por F-G. Entre A e F há vários caminhos (por B ou C, passando por D ou E), que formam ciclos.

- `PONTOS`: ID, nome e tipo de cada ponto.
- `TUBULACOES`: as 10 tubulações da tabela.
- `POSICOES`: coordenadas fixas para o desenho.
- `criar_rede_exemplo()`: devolve uma `Rede` **nova a cada chamada**, para que uma falha simulada em um teste não vaze para outro.

## 4. Algoritmos (`algoritmos/`)

Os três seguem as mesmas regras:

- usam só tubulações ativas, porque consultam a rede por `vizinhos_ativos`;
- não alteram a rede recebida;
- lançam `ValueError` se o ponto informado não existe.

### 4.1 BFS (`bfs.py`)

**Pergunta:** a partir da origem, quais pontos ainda recebem água?

**Como funciona:** visita a rede em camadas usando uma fila. Primeiro a origem, depois os vizinhos dela, depois os vizinhos desses, e assim por diante.

```python
visitados = {origem}
fila = deque([origem])
while fila:
    ponto = fila.popleft()
    ordem_de_visita.append(ponto)
    for vizinho, _distancia in rede.vizinhos_ativos(ponto):
        if vizinho not in visitados:
            visitados.add(vizinho)
            fila.append(vizinho)
```

- O ponto é marcado como visitado **ao entrar na fila**, e não ao sair. Se fosse ao sair, D entraria duas vezes na rede de exemplo (uma vinda de B, outra de C).
- `deque.popleft()` custa O(1); `list.pop(0)` custaria O(V).
- As distâncias são ignoradas. O menor caminho é papel do Dijkstra.

Na rede de exemplo, a partir de R:

| Camada | Pontos |
|---|---|
| 0 | R |
| 1 | A |
| 2 | B, C |
| 3 | D, E |
| 4 | F |
| 5 | G |

Resultado: `['R', 'A', 'B', 'C', 'D', 'E', 'F', 'G']`. Sem R-A, o resultado é só `['R']`.

**Complexidade:** tempo O(V + E), espaço O(V).

### 4.2 Pontes com Tarjan (`pontes.py`)

**Pergunta:** quais tubulações, se falharem sozinhas, dividem a rede?

Uma **ponte** é uma tubulação cuja retirada aumenta o número de partes desconectadas da rede. Na rede de exemplo são R-A e F-G: não existe outro caminho que as substitua.

**Ideia:** fazer uma busca em profundidade (DFS) e guardar dois números por ponto:

- `descoberta[p]`: a ordem em que p foi visitado (0, 1, 2, ...);
- `low[p]`: o menor `descoberta` que p e os pontos abaixo dele na busca conseguem alcançar usando no máximo uma tubulação de retorno (uma tubulação que volta a um ponto já visitado).

A tubulação entre um ponto `pai` e um `filho` da busca é ponte quando:

```text
low[filho] > descoberta[pai]
```

Ou seja, nada abaixo do filho consegue voltar ao pai, nem a algum ponto antes dele, sem passar por essa tubulação.

Na rede de exemplo, com a busca começando em R e seguindo a ordem de cadastro dos vizinhos:

| Ponto | R | A | B | D | C | E | F | G |
|---|---|---|---|---|---|---|---|---|
| `descoberta` | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| `low` | 0 | 1 | 1 | 1 | 1 | 2 | 3 | 7 |

- F-G: `low[G] = 7 > descoberta[F] = 6`, então é ponte.
- R-A: `low[A] = 1 > descoberta[R] = 0`, então é ponte.
- B-D: `low[D] = 1`, que não é maior que `descoberta[B] = 2`. D consegue voltar até A pelo caminho D-C-A, então B-D não é ponte.

**Detalhes da implementação:**

- **Pilha explícita no lugar de recursão.** A versão recursiva clássica passa do limite de recursão do Python (1000 chamadas) em redes longas. Cada item da pilha guarda o que uma chamada recursiva guardaria: `(ponto, ID da tubulação vinda do pai, iterador de vizinhos)`. O iterador lembra até onde os vizinhos já foram examinados. Empilhar um vizinho novo equivale a chamar a função; desempilhar equivale ao retorno, momento em que o `low` é repassado ao pai e a condição de ponte é testada.
- **A volta ao pai é ignorada pelo ID da tubulação, não pelo ponto.** Se um dia a rede aceitar duas tubulações entre o mesmo par, a segunda é um caminho alternativo de verdade e não pode ser descartada.
- **Redes desconexas:** `encontrar_pontes` recomeça a busca em cada ponto ainda não visitado, então todas as partes da rede são analisadas. Isso é comum depois de uma falha.
- O resultado é ordenado com `sorted()`, em ordem de texto. Na R-9, `"T10"` vem antes de `"T2"`.

**Complexidade:** tempo O(V + E), mais O(P log P) para ordenar as P pontes; espaço O(V + E).

### 4.3 Dijkstra (`dijkstra.py`)

**Pergunta:** qual a rota mais curta, em km, entre a origem e o destino?

**Como funciona:**

- Uma fila de prioridade (`heapq`) guarda pares `(distância acumulada, ponto)` e sempre entrega o de menor distância.
- `distancias` guarda a menor distância conhecida até cada ponto; `anteriores`, o ponto anterior nessa rota.
- Ao tirar um ponto da fila, o algoritmo tenta melhorar a distância de cada vizinho. Se melhorar, atualiza `distancias` e `anteriores` e coloca o vizinho na fila.

Detalhes:

- **Entradas antigas.** Um ponto pode entrar mais de uma vez na fila, sempre que se acha uma distância menor até ele. Quando sai uma entrada com distância maior que a registrada, ela é descartada. Isso é mais simples do que alterar um item que já está dentro do `heapq`.
- **Parada antecipada.** Como as distâncias são positivas, quando o destino sai da fila sua distância já é a mínima, e a busca para.
- **Reconstrução do caminho.** Segue `anteriores` do destino até a origem e inverte a lista.
- **Casos especiais.** Sem caminho, devolve `([], None)`; com origem igual ao destino, `([origem], 0)`.
- **Empate.** Com duas rotas de mesma distância, devolve uma delas.

Na rede de exemplo, de R até G, os pontos saem da fila nesta ordem:

```text
R=0  A=2  B=4  C=5  D=6  F=8  E=9  G=10
```

Seguindo `anteriores` a partir de G: G <- F <- D <- B <- A <- R. Resultado: `(['R', 'A', 'B', 'D', 'F', 'G'], 10)`.

Sem B-D, a melhor rota passa a ter 14 km. Existem duas respostas certas: R-A-B-E-F-G e R-A-C-E-F-G.

**Complexidade:** tempo O((V + E) log V), espaço O(V + E). O plano permite `heapq` como estrutura auxiliar.

## 5. Simulação (`servicos/simulacao.py`)

Junta os três algoritmos e compara a rede antes e depois de uma ou mais falhas simultâneas.

### 5.1 `indicadores(rede, origem, destino)`

Roda `bfs`, `dijkstra` e `encontrar_pontes` em uma rede e devolve:

```python
{"alcancaveis": [...], "caminho": [...] ou None, "distancia": km ou None, "pontes": [...]}
```

Quando o Dijkstra não acha caminho, `caminho` e `distancia` ficam `None`. Assim, quem usa o resultado testa só um valor para saber se há rota.

### 5.2 `simular_falhas(rede, origem, destino, tubulacoes_ids)`

1. Valida a origem, o destino e as tubulações. IDs repetidos contam uma vez, e passar um texto (`"T04"`) em vez de uma lista lança `TypeError`, porque o texto seria percorrido letra por letra.
2. `antes = indicadores(rede)`, na rede original.
3. Com a lista vazia, não há falha: o "depois" repete o "antes". É o caso do botão Restaurar.
4. Caso contrário, faz `rede.copiar()`, desativa **todas** as tubulações **na cópia** e calcula `depois = indicadores(copia)`.
5. Compara os dois cenários:
   - `inacessiveis_apos_falha`: pontos alcançáveis antes e não alcançáveis depois, na ordem da BFS;
   - `novas_pontes`: pontes que só existem depois da falha;
   - `pontes_nao_sao_mais`: pontes que deixaram de existir. Por exemplo, a tubulação desativada, quando era ponte: inativa, ela não conta mais.

As pontes são recalculadas porque uma falha pode criar pontes novas. Sem D-F (`T08`), a tubulação E-F (`T09`) vira a única ligação de F com o resto da rede e passa a ser ponte.

**Por que simular falhas juntas.** O efeito de duas falhas não é a soma do efeito de cada uma. D-F e E-F não são pontes: sozinha, qualquer uma delas não desliga ninguém. Juntas, isolam F e G. Do mesmo modo, sem B-D e B-E a rota de 14 km só existe por C (R-A-C-E-F-G), e A-B vira ponte.

O resultado é um dicionário com o antes, o depois e a comparação, incluindo `tubulacoes_interrompidas` (a lista sem repetições). As chaves estão em [combinados.md](combinados.md).

### 5.3 `simular_falha(rede, origem, destino, tubulacao_id)`

Atalho para uma tubulação só: chama `simular_falhas` com `[tubulacao_id]`, ou com `[]` se o ID for `None`, e acrescenta ao resultado a chave `tubulacao_interrompida`. Mantém o contrato original do plano.

**Custo:** uma cópia da rede, F desativações (F = número de falhas, F <= E) e duas rodadas de BFS, Dijkstra e Tarjan: O((V + E) log V).

## 6. Interface

### 6.1 `app.py`

**Como o Streamlit funciona:** a cada clique ou mudança de seleção, o script inteiro roda de novo, de cima a baixo. O que precisa sobreviver entre as execuções fica em `st.session_state`. Aqui são duas listas:

- `selecao_falhas`: o que está marcado na lista de tubulações (o valor do widget);
- `falhas`: as tubulações efetivamente aplicadas na última simulação.

Elas são separadas para que marcar tubulações não simule nada sozinho: a simulação só muda ao clicar em "Simular falhas".

Partes do arquivo:

- **`obter_rede(nome)`**, com `@st.cache_resource`: carrega a rede e calcula o layout do desenho uma única vez por rede. A rede guardada em cache é compartilhada entre execuções e nunca é alterada; é por isso que a simulação trabalha em cópias.
- **Barra lateral:**
  - seleção da rede (R-9 ou exemplo). Trocar de rede apaga as falhas e a seleção;
  - origem e destino, e uma lista de múltipla escolha (`st.multiselect`) com as tubulações. Tudo em ordem natural com `ordenar_ids`: R primeiro, depois 1, 2, ..., 10 (e T1, T2, ..., T10), e não a ordem de texto, que poria 10 antes de 2;
  - **Simular falhas** copia a seleção para `falhas`. Fica desativado enquanto nada estiver marcado;
  - **Restaurar rede** esvazia `falhas` e desmarca a lista;
  - quando a seleção é diferente das falhas aplicadas, aparece o aviso "A seleção mudou".
- **Por que os botões usam `on_click`:** o Streamlit só permite mudar o valor de um widget por código antes de ele ser desenhado naquela execução. As funções de `on_click` (`aplicar_falhas` e `limpar_falhas`) rodam antes do script, então podem limpar a seleção sem erro.
- **Área principal:**
  - mensagem de estado: rede original ou lista das tubulações interrompidas;
  - três métricas: distância antes, distância depois e número de pontos inacessíveis. A diferença de distância só aparece quando há falha e as duas distâncias existem;
  - aviso de "sem caminho" quando o destino fica isolado;
  - dois desenhos lado a lado, antes e depois, com zoom (seção 6.3). As figuras são convertidas em SVG e fechadas logo depois (`plt.close`) para liberar memória. A página é exibida por `mostrar_html`, que usa `st.iframe` nas versões novas do Streamlit e `st.components.v1.html` nas antigas;
  - detalhes: caminhos, pontes, pontos inacessíveis e pontes novas.
- **Erros:** um `ValueError` ao carregar a rede ou ao simular aparece como mensagem na tela (`st.error`), e a execução para (`st.stop`).

### 6.2 `visualizacao.py`

**`calcular_layout(rede, semente=7, iteracoes=400)`**

A R-9 não tem coordenadas, então as posições dos pontos são calculadas por um **layout de forças** (no estilo Fruchterman-Reingold), escrito com `numpy`:

- os pontos começam em posições aleatórias, com semente fixa: o desenho sai igual em toda execução;
- todo par de pontos se repele com força `k² / d`, e toda tubulação puxa suas pontas com força `d² / k`, em que `d` é a distância no desenho e `k` é a distância ideal entre pontos;
- a cada passo, cada ponto anda no máximo uma "temperatura", que diminui 1,5% por passo: o desenho começa mexendo bastante e vai se estabilizando;
- no fim, as posições são levadas para o intervalo de 0 a 1, e uma última passada afasta pontos muito próximos para os círculos não se sobreporem.

O custo é O(iterações x V²). Para 62 pontos é rápido, e o cache do `app.py` faz o cálculo rodar uma vez só. **As posições servem só para o desenho: o comprimento das linhas não representa os km.**

**`desenhar_rede(...)`**

Desenha uma linha por tubulação, com prioridade de estilo:

| Prioridade | Situação | Estilo |
|---|---|---|
| 1 | Tubulação interrompida (parâmetro `falhas`, uma ou mais) | vermelho tracejado |
| 2 | Parte do menor caminho | verde grosso |
| 3 | Ponte | laranja |
| 4 | Demais | cinza fino |

- Os pontos inacessíveis ficam cinza claro, a origem fica azul escuro e os demais azul claro. Origem e destino têm borda mais grossa.
- A distância em km aparece nas tubulações interrompidas e nos trechos do caminho, mas só quando o caminho tem até 6 trechos, para os rótulos não se sobreporem.
- As arestas do caminho são comparadas como `frozenset` de duas pontas, então a ordem (A-B ou B-A) não importa.
- Cada elemento recebe um `gid`, que vira o `id` do grupo no SVG: `aresta-T1`, `no-R`, `rotulo-R` e `km-T1`. O zoom usa esses nomes para achar cada parte do desenho.
- Com `legenda=False`, a legenda não é desenhada; a página com zoom tem a sua, fora do desenho, para não sumir ao aproximar.
- Devolve uma figura do Matplotlib.

### 6.3 Zoom nos desenhos (`figura_para_svg` e `html_com_zoom`)

O `st.pyplot` mostra uma imagem PNG fixa, sem zoom. Ampliar uma imagem também não resolveria o problema de pontos muito próximos: círculos e linhas cresceriam na mesma proporção, e pontos sobrepostos continuariam sobrepostos. Por isso a interface usa outro caminho:

1. **`figura_para_svg(fig)`** salva a figura do Matplotlib como SVG (desenho vetorial, em texto) e tira a largura e a altura fixas, para o tamanho vir da página.
2. **`html_com_zoom(svgs, titulos, altura, chave)`** monta uma página HTML com os SVGs lado a lado, os títulos, a legenda, os botões e um script em JavaScript que faz o zoom.

**Como o zoom funciona:**

- O SVG tem uma "janela" (`viewBox`) que diz qual parte do desenho aparece. Aproximar é diminuir essa janela em volta do cursor; arrastar é deslocá-la. A janela nunca sai dos limites do desenho.
- Para separar pontos próximos, círculos, textos e linhas crescem bem menos que as distâncias. Com zoom Z, as distâncias crescem Z vezes e os elementos crescem Z^0,25 vezes: a 5x, as distâncias ficam 5x maiores e os círculos só ~1,5x. Para isso, a cada zoom o script reduz cada ponto, ID e rótulo de km em volta de uma âncora, e afina as linhas e o tracejado na mesma proporção.
- A âncora do ID é o centro do seu ponto, e a do rótulo de km é o meio da sua tubulação. Se fosse o centro do próprio texto, a pequena distância entre o texto e o ponto cresceria com o zoom, e o texto sairia de dentro do círculo.
- Os dois desenhos usam a mesma janela, então o zoom e o arraste valem para os dois ao mesmo tempo: dá para comparar a mesma região antes e depois.
- O zoom fica guardado no `sessionStorage` do navegador, separado por rede. Como a página é recriada a cada clique no app, isso mantém o zoom ao simular outra falha.

**Controles:** rolar o mouse aproxima ou afasta em volta do cursor (até 25x), arrastar move, dois cliques voltam à rede inteira. Os botões +, - e Ajustar fazem o mesmo, e o nível atual aparece ao lado deles.

## 7. Desempenho (`desempenho/`)

### 7.1 `testar_desempenho_dijkstra.py`

Mede o tempo do Dijkstra na R-9 e em redes sintéticas maiores.

- **`gerar_grafo_conexo(n, fator_arestas=3, semente)`** monta uma rede artificial:
  - primeiro uma corrente 0-1-2-...-(n-1), que garante que tudo está ligado;
  - depois tubulações extras entre pontos a no máximo 40 posições de distância, até ter 3n tubulações. As ligações ficam locais, como em uma rede de tubos, sem atalhos entre pontos distantes;
  - distâncias aleatórias entre 0,1 e 10 km, com semente fixa, para a medição poder ser repetida.
- **`medir(rede, origem, destino)`**: roda 5 vezes sem medir (aquecimento), depois mede 30 execuções com `time.perf_counter_ns` e calcula mediana, média, mínimo e máximo. Também confere se o caminho encontrado começa na origem e termina no destino.
- **`executar()`**: mede a R-9 (R até o ponto 20) e redes de 100, 500, 1000 e 5000 pontos, e grava `resultados_desempenho_dijkstra.csv` com o sistema, o processador e a versão do Python.

### 7.2 `gerar_grafico_desempenho.py`

Lê o CSV e gera `grafico_desempenho_dijkstra.png`, um gráfico de barras com a mediana de cada rede.

### 7.3 Resultados registrados

Do CSV atual, medido pelo integrante 3. Essa versão do CSV não registra o computador; as próximas execuções registram.

| Rede | Pontos | Tubulações | Mediana (ms) |
|---|---|---|---|
| R-9 | 62 | 72 | 0,065 |
| Sintética | 100 | 300 | 0,183 |
| Sintética | 500 | 1500 | 0,973 |
| Sintética | 1000 | 3000 | 2,169 |
| Sintética | 5000 | 15000 | 17,629 |

## 8. Testes (`testes/`)

Rodar na raiz: `python -m unittest discover -s testes -t . -v`. São 90 testes.

| Arquivo | Testes | O que confere |
|---|---|---|
| `test_rede.py` | 16 | Cadastro, validações, ativar/desativar e independência da cópia |
| `test_leitura_csv.py` | 15 | Leitura da R-9 (62 pontos, 72 tubulações) e rejeição de CSVs inválidos com a linha do erro |
| `test_bfs.py` | 10 | Cenários do plano, ordem por camadas, tubulação inativa, rede desconexa, rede não alterada |
| `test_pontes.py` | 13 | Cenários do plano, ciclo, árvore, rede desconexa, caminho de 5000 pontos e comparação com força bruta |
| `test_dijkstra.py` | 12 | 10 km, 14 km com rota empatada, destino inacessível, origem igual ao destino, pontos inexistentes |
| `test_simulacao.py` | 18 | Cenários da página 6 do plano, ponte nova após falha, falhas múltiplas (rota alternativa, isolamento de F e G), IDs repetidos ou inválidos, rede original preservada |
| `test_integracao_r9.py` | 6 | Todos os módulos juntos na R-9: R até 20 com 7,635 km, pontes T1 e T8, falhas em T1 e T8, separadas e juntas |

Apoios em `auxiliares.py`:

- `montar_rede(pontos, tubulacoes)`: monta uma rede de teste a partir de listas;
- `rede_por_pares("A-B B-C")`: monta uma rede pequena em uma linha de texto;
- `criar_rede_exemplo()`: a rede do plano, vinda de `exemplos/rede_exemplo.py`;
- `retrato_da_rede(rede)`: resume todo o estado da rede em uma estrutura comparável. Tira-se um retrato antes e outro depois de rodar um algoritmo; se forem iguais, o algoritmo não alterou a rede.

Duas verificações merecem destaque:

- **Força bruta nas pontes.** `test_pontes.py` aplica a definição de ponte diretamente: desativa cada tubulação em uma cópia e conta se o número de partes da rede aumentou. O resultado é comparado com o Tarjan na rede de exemplo com cada falha, em redes pequenas variadas e em 100 redes aleatórias.
- **Caminho de 5000 pontos.** Uma rede em linha obriga a busca a descer 5000 níveis. O teste garante que o Tarjan não estoura o limite de recursão do Python.

## 9. Script auxiliar (`scripts/visualizar_rede.py`)

Lista no terminal os pontos e as tubulações da R-9 e gera `docs/imagens/rede_r9.dot`, um arquivo para o Graphviz em que o reservatório aparece em dourado. A imagem `docs/imagens/rede_r9.svg` foi gerada a partir dele. Não faz parte da aplicação; serve para conferir a base e produzir figuras para o relatório.

Rodar na raiz: `python -m scripts.visualizar_rede`.

## 10. Decisões de projeto e limites

**Decisões:**

- **Lista de adjacência com dicionários.** A R-9 é esparsa (72 tubulações para 62 pontos). Uma matriz de adjacência teria 62 x 62 posições, quase todas vazias. Com dicionários, saber se dois pontos estão ligados custa O(1) e listar vizinhos custa O(grau).
- **Desativar em vez de remover.** Uma falha só muda o campo `ativa`. A tubulação continua cadastrada e a falha pode ser desfeita.
- **Uma cópia por simulação.** A rede original nunca muda, o que torna o Restaurar trivial e evita que uma falha "vaze" para a simulação seguinte.
- **IDs como texto.** Os IDs da R-9 são números, mas ficam como texto (`"1"`, `"T1"`) para que todos os módulos usem o mesmo tipo.
- **Retornos em lista.** BFS e pontes devolvem listas, para manter a ordem de visita e um resultado previsível. Quem precisa de operações de conjunto converte com `set(...)`.
- **Estrutura e algoritmos próprios.** NetworkX não é usado, conforme o enunciado. `numpy` entra só no cálculo das posições do desenho, e `heapq` é a fila de prioridade do Dijkstra.

**Limites:**

- O sistema analisa conectividade e distância. Não calcula pressão nem vazão: ter um caminho no grafo não garante abastecimento real.
- A capacidade nominal das tubulações não é modelada. A base preparada não tem esse dado e ele não foi inventado.
- As falhas de uma simulação acontecem ao mesmo tempo e são sempre comparadas com a rede original. Não há sequência no tempo (uma falha depois da outra).
- O desenho da R-9 é esquemático; as posições não são geográficas.
- Com rotas empatadas, o Dijkstra mostra só uma delas.
