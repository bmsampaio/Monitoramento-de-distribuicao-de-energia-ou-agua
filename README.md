# Sistema Inteligente de Monitoramento e Análise de Falhas em Redes de Distribuição de Água

Projeto acadêmico desenvolvido em grupo para a disciplina de **Teoria dos Grafos e Computabilidade**, no tema **Monitoramento de Distribuição de Energia ou Água**, com foco em redes de distribuição de água.

A aplicação utiliza grafos para representar a rede, consultar conexões, calcular caminhos de menor distância e avaliar o impacto da interrupção de tubulações. Os modelos e algoritmos foram implementados em **Python**, sem bibliotecas específicas para processamento de grafos, e a visualização é feita por uma interface em **Streamlit**.

> **Escopo:** o sistema analisa a conectividade e as distâncias das tubulações. Não simula pressão, vazão ou outros fenômenos hidráulicos.

## Funcionalidades

- **Visualização da rede** e de suas tubulações por meio de uma interface gráfica.
- **Seleção de origem e destino** para consultar a conectividade e os caminhos disponíveis.
- **Busca dos pontos alcançáveis** a partir do reservatório ou de outro vértice selecionado.
- **Cálculo do caminho de menor distância**, considerando o comprimento das tubulações.
- **Identificação de tubulações críticas (pontes)**, cuja remoção aumenta o número de componentes conexas.
- **Simulação da interrupção de uma tubulação** e comparação dos resultados antes e depois da falha.
- **Destaque de pontos inacessíveis e alterações na rede**, facilitando a interpretação das consequências da falha.

Cada simulação é realizada sobre uma **cópia independente da rede**: a tubulação é desativada no cenário de teste, enquanto os dados originais permanecem preservados.

## Tecnologias utilizadas

| Tecnologia | Utilização |
| --- | --- |
| Python 3 | Modelos, leitura de dados, algoritmos e simulação |
| Streamlit | Interface interativa |
| Matplotlib | Representação visual da rede |
| openpyxl | Leitura da planilha original da base R-9 |
| CSV | Armazenamento dos nós e das tubulações preparados |
| `unittest` | Testes automatizados |

A estrutura do grafo e os algoritmos **BFS, Dijkstra e Tarjan** foram desenvolvidos no projeto, sem uso de NetworkX para realizar essas operações.

## Divisão do trabalho

| Integrante | Nome | Responsabilidade principal |
|---|---|---|
| 1 | Bárbara Portes | Modelos, estrutura da rede e leitura dos dados, Modelagem do grafo |
| 2 | Thiago | BFS e identificação de pontes |
| 3 | Felipe | Dijkstra e avaliação de desempenho |
| 4 | Augusto Gonçalves | Interface e visualização |
| 5 | João Victor dos Santos Nogueira | Simulação de falhas e integração 

> **Observação:** Apesar da divisão de responsabilidades, este é um trabalho em grupo. Todos devem se ajudar, participar das revisões e colaborar na integração. Cada integrante precisa compreender o projeto completo, e não apenas sua parte, para explicar as decisões do grupo e participar das apresentações com segurança.

## Modelagem da rede

A rede é representada por um **grafo não direcionado e ponderado**.

| Conceito do grafo | Representação no projeto |
| --- | --- |
| Vértice | Reservatório ou ponto de demanda |
| Aresta | Tubulação que conecta dois pontos |
| Peso | Comprimento da tubulação, em quilômetros |
| Estado da aresta | Tubulação ativa ou inativa |

A estrutura utiliza uma **lista de adjacência com dicionários Python**. Como as conexões são não direcionadas, uma tubulação entre os pontos `4` e `7` é registrada nos dois sentidos. O comprimento e o estado ficam associados ao objeto da tubulação, evitando duplicação dessas informações.

Os principais modelos são:

- `No`: identificador, nome e tipo do ponto.
- `Tubulacao`: identificador, extremidades, distância e estado.
- `Rede`: cadastro de vértices e tubulações, adjacência, consulta de vizinhos ativos, alteração do estado e cópia da rede.

Uma tubulação inativa continua cadastrada, mas **não é considerada** pelos algoritmos que consultam `vizinhos_ativos`.

## Algoritmos

| Algoritmo | Objetivo |
| --- | --- |
| **Busca em largura (BFS)** | Identificar os vértices alcançáveis a partir de uma origem, usando apenas tubulações ativas |
| **Dijkstra** | Calcular o caminho de menor distância entre origem e destino, usando o comprimento das tubulações como peso |
| **Tarjan (busca em profundidade)** | Identificar pontes: tubulações cuja interrupção isolada separa componentes da rede |

Todos os algoritmos consideram o estado das tubulações. Após uma falha, a conectividade, os caminhos e as pontes podem mudar; por isso, os resultados são novamente calculados no cenário simulado.

## Base de dados R-9

O projeto utiliza a rede de referência **R-9**, disponibilizada no [Mendeley Data](https://data.mendeley.com/datasets/zyg68ck8xc/1).

| Informação | Quantidade |
| --- | ---: |
| Vértices | **62** |
| Reservatórios | **1** |
| Pontos de demanda | **61** |
| Tubulações | **72** |

O arquivo original `R9_water_distribution_network_input_data.xlsx` é preparado pelo script `scripts/preparar_r9_dataset.py`, que gera:

- `dados/nos.csv`, com as colunas `id,nome,tipo`;
- `dados/tubulacoes.csv`, com as colunas `id,origem,destino,distancia_km,ativa`.

Na preparação, o reservatório recebe o identificador `R`, os comprimentos são convertidos de metros para quilômetros, os IDs são padronizados como texto e as tubulações são inicialmente marcadas como ativas.

O carregamento dos CSVs em objetos da classe `Rede` é realizado separadamente, com conversão dos dados e validação de conexões inválidas.

**Fonte:** [R-9 no Mendeley Data — versão 1](https://doi.org/10.17632/zyg68ck8xc.1).

## Organização do projeto

```text
.
├── app.py                       # Interface Streamlit
├── visualizacao.py              # Desenho e destaques da rede
├── modelos/
│   ├── no.py                    # Classe No
│   ├── tubulacao.py             # Classe Tubulacao
│   └── rede.py                  # Classe Rede e lista de adjacência
├── algoritmos/
│   ├── bfs.py                   # Busca em largura
│   ├── dijkstra.py              # Caminho mínimo
│   └── pontes.py                # Identificação de pontes
├── servicos/
│   ├── leitura_csv.py           # Carregamento e validação dos CSVs
│   └── simulacao.py             # Comparação antes/depois da falha
├── scripts/
│   └── preparar_r9_dataset.py   # Preparação da planilha R-9
├── dados/
│   ├── originais/              # Planilha de origem
│   ├── nos.csv
│   └── tubulacoes.csv
├── exemplos/                    # Rede pequena para verificações
├── testes/                      # Testes automatizados
├── docs/                        # Diagramas, imagens e relatório
├── requirements.txt
└── README.md
```

A árvore apresenta a organização documentada do projeto; arquivos auxiliares e materiais acadêmicos podem variar conforme a versão do repositório.

## Como executar

### 1. Obter o projeto

```bash
git clone https://github.com/bmsampaio/Monitoramento-de-distribuicao-de-energia-ou-agua.git
cd Monitoramento-de-distribuicao-de-energia-ou-agua
```

### 2. Criar e ativar um ambiente virtual

**Linux / macOS / WSL:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Preparar os dados (quando necessário)

Se os CSVs já estiverem disponíveis em `dados/`, esta etapa pode ser dispensada. Para gerá-los a partir da planilha original, coloque `R9_water_distribution_network_input_data.xlsx` em `dados/originais/` e execute:

```bash
python scripts/preparar_r9_dataset.py
```

A preparação gera os arquivos `dados/nos.csv` e `dados/tubulacoes.csv`.

### 5. Iniciar a aplicação

```bash
python -m streamlit run app.py
```

O Streamlit exibirá no terminal o endereço local para abrir a interface no navegador.

## Exemplo de análise: falha da tubulação T8

Na rede R-9 original, todos os **62 vértices** são alcançáveis a partir do reservatório `R`. A análise identifica duas pontes: **T1** (entre `R` e `1`) e **T8** (entre os pontos `4` e `7`).

Para observar o efeito de uma interrupção na interface:

1. Selecione o reservatório `R` como origem.
2. Selecione o ponto `20` como destino.
3. Escolha a tubulação `T8` para a simulação.
4. Execute a análise e compare os cenários.

**Resultado documentado:** ao desativar a T8, **20 pontos de demanda** (de `7` a `26`) ficam desconectados do reservatório, incluindo o ponto `20`. Isso exemplifica por que a T8 é considerada uma ponte do grafo.

A identificação de uma conexão no grafo indica um caminho estrutural possível, **não** a garantia de abastecimento físico.

## Testes automatizados

Na pasta raiz do projeto, execute:

```bash
python -m unittest discover -s testes -v
```

Os testes documentados cobrem, entre outros aspectos:

- cadastro e validação dos pontos e das tubulações;
- consulta das conexões nos dois sentidos e filtragem de tubulações inativas;
- independência entre a rede original e a cópia utilizada na simulação;
- carregamento e validação dos arquivos CSV;
- comportamento da BFS em redes conectadas e desconectadas;
- detecção de pontes em árvores, ciclos e redes desconectadas;
- comparação de resultados com exemplos de referência, incluindo a rede R-9.

## Limitações

- **Sem simulação hidráulica:** não são calculadas pressão, vazão, capacidade de tubulações ou demanda atendida.
- **Falhas isoladas:** a simulação apresentada compara a rede original com a interrupção de uma tubulação por vez; falhas simultâneas não são analisadas diretamente.
- **Tubulações críticas, não pontos críticos:** o algoritmo de pontes não identifica pontos de articulação.
- **Desenho esquemático:** a posição dos vértices na visualização não deve ser interpretada como localização geográfica real.

## Contexto acadêmico

Este é um trabalho em grupo da disciplina de **Teoria dos Grafos e Computabilidade**. As atividades abrangeram modelagem, preparação de dados, implementação dos algoritmos, visualização, simulação, testes e documentação.

Para detalhes de metodologia, análises e limitações, consulte o relatório acadêmico do projeto, quando disponibilizado na pasta `docs/`.
