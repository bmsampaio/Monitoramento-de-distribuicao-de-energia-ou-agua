# Monitoramento de redes de distribuição de água

Projeto da disciplina de **Teoria dos Grafos**, desenvolvido por cinco integrantes.

O objetivo é analisar uma rede de água usando grafos: identificar pontos desconectados, calcular caminhos mínimos e simular falhas em tubulações.

## Tecnologias

- **Python:** implementação dos modelos e algoritmos.
- **Streamlit:** interface gráfica.
- **Matplotlib:** visualização da rede.
- **openpyxl:** leitura da planilha original para gerar os CSVs.

A estrutura do grafo e os algoritmos serão implementados pelo grupo, sem NetworkX.

## Modelagem

Utilizamos um **grafo não direcionado e ponderado**:

- **Nós:** reservatório e pontos da rede.
- **Arestas:** tubulações.
- **Peso:** distância em quilômetros.
- **Estado:** tubulação ativa ou inativa.

A rede utiliza uma lista de adjacência com dicionários Python.

O projeto analisa conectividade e distância. Não realiza cálculos hidráulicos de pressão ou vazão.

## Divisão do trabalho

| Integrante | Responsabilidade |
|---|---|
| 1 — Bárbara | Modelos, estrutura da rede e leitura dos CSVs |
| 2 — A preencher | BFS e Tarjan para identificação de pontes |
| 3 — A preencher | Dijkstra e avaliação de desempenho |
| 4 — A preencher | Interface Streamlit e visualização |
| 5 — A preencher | Simulação de falhas e integração |

Todos participam dos testes, da documentação e das apresentações.

## Organização do projeto

| Caminho | Conteúdo |
|---|---|
| `modelos/` | Classes `No`, `Tubulacao` e `Rede` |
| `algoritmos/` | BFS, Dijkstra e identificação de pontes |
| `servicos/` | Leitura dos CSVs e simulação de falhas |
| `scripts/` | Preparação da base de dados |
| `dados/originais/` | Planilha original |
| `dados/` | Arquivos `nos.csv` e `tubulacoes.csv` |
| `testes/` | Testes dos módulos |
| `docs/` | Diagramas e relatório |
| `app.py` | Interface da aplicação |
| `visualizacao.py` | Desenho da rede |

## Base de dados

Utilizamos a base **R-9**, com **62 nós e 72 tubulações**.

Fonte: https://data.mendeley.com/datasets/zyg68ck8xc/1

O script `scripts/preparar_r9_dataset.py` converte a planilha original em dois arquivos:

**`dados/nos.csv`**

```csv
id,nome,tipo
```

**`dados/tubulacoes.csv`**

```csv
id,origem,destino,distancia_km,ativa
```

As distâncias são convertidas de metros para quilômetros. Os identificadores são strings e todas as tubulações começam ativas.

## Como utilizar a classe Rede

| Método | Função |
|---|---|
| `adicionar_no(no)` | Cadastra um nó |
| `adicionar_tubulacao(tubulacao)` | Cadastra uma conexão nos dois sentidos |
| `vizinhos_ativos(identificador)` | Retorna pares `(vizinho, distancia)` das conexões ativas |
| `alterar_estado(identificador, ativa)` | Ativa ou desativa uma tubulação |
| `copiar()` | Cria uma rede independente |

Exemplo:

```python
from modelos.no import No
from modelos.tubulacao import Tubulacao
from modelos.rede import Rede

rede = Rede()

rede.adicionar_no(No("R", "Reservatório", "reservatorio"))
rede.adicionar_no(No("A", "Ponto A", "ponto_demanda"))

rede.adicionar_tubulacao(
    Tubulacao("T1", "R", "A", 2.0, True)
)

print(rede.vizinhos_ativos("R"))
# [("A", 2.0)]

cenario = rede.copiar()
cenario.alterar_estado("T1", False)
# A rede original permanece inalterada.
```

### Combinados para integração

- Cadastrar os nós antes das tubulações.
- Usar identificadores como strings e distâncias em quilômetros.
- Usar `True` e `False` para o estado das tubulações.
- Consultar `vizinhos_ativos` nos algoritmos para ignorar conexões desativadas.
- Aplicar falhas em uma cópia da rede.
- Avisar os colegas antes de alterar nomes ou retornos compartilhados.

A leitura dos CSVs deverá converter as distâncias para números e os textos `true` e `false` para booleanos.

## Preparar o ambiente

Na raiz do repositório:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Para executar a preparação dos dados:

```bash
python -m pip install openpyxl
python scripts/preparar_r9_dataset.py
```

A planilha `R9_water_distribution_network_input_data.xlsx` deve estar em `dados/originais/`.

As demais dependências deverão ser registradas no `requirements.txt`. Para instalá-las:

```bash
python -m pip install -r requirements.txt
```

Quando a interface estiver implementada:

```bash
python -m streamlit run app.py
```

## Andamento da estrutura e dos dados

- [x] Preparação dos CSVs da R-9.
- [x] Implementação dos modelos `No`, `Tubulacao` e `Rede`.
- [ ] Testes da classe `Rede`.
- [ ] Carregamento dos CSVs em uma rede.
- [ ] UML de classes.

Os responsáveis pelos demais módulos deverão atualizar seu andamento conforme o desenvolvimento.

## Colaboração

- Criar uma branch por funcionalidade.
- Fazer commits individuais e descritivos.
- Revisar as alterações por pull request.
- Testar os módulos antes da integração.
- Não enviar `.venv/` e `__pycache__/` para o Git.

## Entrega

**Data prevista:** 22/11/2026, a confirmar no Canvas.

- Código-fonte e histórico Git.
- Interface funcional.
- Relatório de 12 a 15 páginas em LaTeX no template SBC.
- Apresentação presencial de 10 minutos.
- Vídeo de demonstração de 12 a 18 minutos.
- Entrega individual no Canvas conforme o enunciado.
