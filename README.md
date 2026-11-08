# Monitoramento de redes de distribuição de água

Projeto da disciplina de **Teoria dos Grafos**, desenvolvido por cinco integrantes.

**Tema:** Tema 4 — Monitoramento de distribuição de energia ou água.  
**Aplicação escolhida:** rede de distribuição de água.  
**Nome provisório:** Sistema Inteligente de Monitoramento e Análise de Falhas em Redes de Distribuição de Água.

## 1. Objetivo

Desenvolver uma aplicação que permita visualizar uma rede de distribuição de água, calcular caminhos e analisar as consequências da interrupção de tubulações.

O sistema deverá responder:

- Quais pontos estão conectados ao reservatório?
- Quais pontos ficam inacessíveis após uma falha?
- Existe um caminho alternativo até o destino?
- Qual caminho possui a menor distância?
- Quais tubulações são críticas para a conectividade?

O projeto está em desenvolvimento. As funcionalidades planejadas e as implementações disponíveis estão identificadas abaixo.

## 2. Como a rede é representada

Utilizamos um **grafo não direcionado e ponderado**.

| Elemento | Representação |
|---|---|
| Nó ou vértice | Reservatório ou outro ponto da rede |
| Aresta | Tubulação entre dois nós |
| Peso | Distância da tubulação em quilômetros |
| Estado | Tubulação ativa ou inativa |

A estrutura é uma **lista de adjacência implementada com dicionários Python**.

Como o grafo não é direcionado, uma tubulação entre R e A é registrada nos dois sentidos: R → A e A → R.

### Simplificações e limites

O sistema analisa a conectividade estrutural da rede.

Não serão calculadas pressão, vazão ou capacidade de atendimento da demanda. A existência de um caminho no grafo não garante que o abastecimento seja fisicamente possível.

A versão atual do modelo não possui um atributo de capacidade nominal. Esse dado não é necessário para os algoritmos escolhidos e não será inventado para preencher informações ausentes.

A primeira versão da comparação deverá analisar uma falha por vez, preservando a rede original.

## 3. Tecnologias

| Tecnologia | Finalidade |
|---|---|
| Python 3 | Implementação da aplicação |
| Streamlit | Interface gráfica planejada |
| Matplotlib | Visualização planejada da rede |
| openpyxl | Leitura da planilha original da base R-9 |
| CSV | Armazenamento dos dados preparados |
| Git | Controle de versão e colaboração |
| LaTeX | Relatório final no template SBC |

Os algoritmos e a estrutura do grafo serão implementados pelo grupo.

**Não utilizar NetworkX ou bibliotecas equivalentes para criar ou processar o grafo da aplicação.** Conforme o enunciado, essas bibliotecas podem ser utilizadas apenas para comparação de desempenho.

Módulos gerais do Python, como `csv`, `pathlib`, `collections` e `heapq`, podem apoiar o desenvolvimento.

O `openpyxl` será utilizado somente para ler a planilha. Ele não implementará a estrutura do grafo nem seus algoritmos.

## 4. Divisão do trabalho

| Integrante | Nome | Responsabilidade principal |
|---|---|---|
| 1 | Bárbara | Modelos, estrutura da rede e leitura dos dados |
| 2 | A preencher | BFS e identificação de pontes |
| 3 | A preencher | Dijkstra e avaliação de desempenho |
| 4 | A preencher | Interface e visualização |
| 5 | A preencher | Simulação de falhas e integração 

> **Observação:** Apesar da divisão de responsabilidades, este é um trabalho em grupo. Todos devem se ajudar, participar das revisões e colaborar na integração. Cada integrante precisa compreender o projeto completo, e não apenas sua parte, para explicar as decisões do grupo e participar das apresentações com segurança.

### Integrante 1 — estrutura e dados

- Implementar `No`, `Tubulacao` e `Rede`.
- Preparar os CSVs da base escolhida.
- Implementar o carregamento dos CSVs em uma rede.
- Validar os dados de entrada.
- Testar cadastro, consulta, alteração de estado e cópia.
- Produzir o UML de classes.
- Documentar a modelagem e as adaptações da base.

### Integrante 2 — conectividade e pontes

- Implementar BFS para identificar os nós alcançáveis.
- Implementar Tarjan para identificar pontes.
- Considerar somente tubulações ativas.
- Testar redes conectadas, desconexas, árvores e ciclos.
- Documentar os algoritmos, suas complexidades e resultados.

### Integrante 3 — caminhos mínimos e desempenho

- Implementar Dijkstra usando distância como peso.
- Tratar destinos inacessíveis e origem igual ao destino.
- Testar caminhos mínimos e rotas empatadas.
- Organizar medições de desempenho com apoio dos demais integrantes.
- Documentar o algoritmo e os resultados.

### Integrante 4 — interface e visualização

- Desenvolver a interface em Streamlit.
- Desenhar a rede com Matplotlib.
- Criar seletores de origem, destino e tubulação.
- Destacar caminhos, pontes e conexões interrompidas.
- Exibir os resultados da comparação.
- Produzir casos de uso e capturas da aplicação.

### Integrante 5 — simulação e integração

- Implementar a comparação antes e depois de uma falha.
- Utilizar uma cópia independente da rede.
- Integrar BFS, Dijkstra e identificação de pontes.
- Identificar os novos pontos inacessíveis.
- Comparar distâncias quando houver caminhos nos dois cenários.
- Coordenar os testes de integração.
- Organizar o roteiro conjunto de demonstração.

### Responsabilidades de todos

Cada integrante deverá:

- Planejar, implementar, testar e documentar sua parte.
- Fazer commits individuais e descritivos.
- Revisar o trabalho de um colega.
- Contribuir para o relatório.
- Participar da apresentação presencial e do vídeo.
- Corrigir problemas de seu módulo durante a integração.

O relatório não será responsabilidade exclusiva de uma pessoa.

## 5. Organização dos arquivos

A organização abaixo orienta o projeto. Alguns arquivos ainda serão implementados.

| Caminho | Conteúdo |
|---|---|
| `app.py` | Interface Streamlit |
| `visualizacao.py` | Desenho da rede com Matplotlib |
| `modelos/no.py` | Classe `No` |
| `modelos/tubulacao.py` | Classe `Tubulacao` |
| `modelos/rede.py` | Classe `Rede` |
| `algoritmos/bfs.py` | Busca em largura |
| `algoritmos/dijkstra.py` | Caminho mínimo |
| `algoritmos/pontes.py` | Identificação de pontes |
| `servicos/leitura_csv.py` | Carregamento dos CSVs em uma rede |
| `servicos/simulacao.py` | Comparação dos cenários |
| `scripts/preparar_r9_dataset.py` | Conversão da planilha R-9 para CSV |
| `dados/originais/` | Dados originais e identificação da fonte |
| `dados/nos.csv` | Nós preparados para a aplicação |
| `dados/tubulacoes.csv` | Tubulações preparadas para a aplicação |
| `exemplos/rede_exemplo.py` | Rede fictícia pequena para testes |
| `testes/` | Testes dos módulos e da integração |
| `docs/combinados.md` | Contratos e decisões compartilhadas |
| `docs/diagramas/` | UML e casos de uso |
| `docs/imagens/` | Capturas da aplicação |
| `docs/relatorio/` | Arquivos do relatório |
| `requirements.txt` | Dependências externas |
| `.gitignore` | Arquivos que não devem entrar no Git |
| `README.md` | Visão geral e instruções do projeto |

As pastas de módulos podem conter arquivos `__init__.py` vazios para organizá-las como pacotes Python.

Pastas vazias não são registradas pelo Git. Quando necessário, usar um arquivo `.gitkeep`.

## 6. Modelos implementados

### Classe No

Representa um ponto da rede.

| Atributo | Conteúdo |
|---|---|
| `identificador` | Identificador do nó, como `"R"` ou `"1"` |
| `nome` | Nome descritivo |
| `tipo` | Categoria, como `reservatorio` ou `ponto_demanda` |

### Classe Tubulacao

Representa uma conexão entre dois nós.

| Atributo | Conteúdo |
|---|---|
| `identificador` | Identificador da tubulação, como `"T1"` |
| `origem` | Identificador de uma extremidade |
| `destino` | Identificador da outra extremidade |
| `distancia` | Distância em quilômetros |
| `ativa` | `True` para ativa e `False` para inativa |

Os nomes `origem` e `destino` identificam as extremidades. Eles não impõem um sentido ao grafo.

### Classe Rede

Organiza os dados em três dicionários:

| Atributo | Estrutura |
|---|---|
| `vertices` | Identificador do nó → objeto `No` |
| `tubulacoes` | Identificador da tubulação → objeto `Tubulacao` |
| `adjacencia` | Identificador do nó → dicionário de vizinhos e IDs das tubulações |

Exemplo de adjacência de uma tubulação T1 entre R e A:

```python
{
    "R": {"A": "T1"},
    "A": {"R": "T1"}
}
```

### Métodos da Rede

| Método | Comportamento |
|---|---|
| `adicionar_no(no)` | Cadastra um nó |
| `adicionar_tubulacao(tubulacao)` | Cadastra a tubulação e registra a conexão nos dois sentidos |
| `vizinhos_ativos(identificador)` | Retorna uma lista de pares `(vizinho, distancia)` |
| `alterar_estado(identificador, ativa)` | Altera o estado de uma tubulação |
| `copiar()` | Retorna uma rede independente, com novos objetos |

Os métodos de cadastro e alteração não possuem retorno explícito. Em caso de sucesso, retornam `None`.

As validações implementadas lançam `ValueError` quando encontram:

- Identificadores duplicados no respectivo cadastro.
- Origem ou destino inexistente.
- Origem igual ao destino.
- Distância menor ou igual a zero.
- Outra tubulação entre o mesmo par de nós, inclusive no sentido inverso.
- Nó inexistente na consulta de vizinhos.
- Tubulação inexistente na alteração de estado.

### Cuidados ao utilizar os modelos

- Cadastrar os nós antes das tubulações.
- Utilizar identificadores como strings.
- Passar a distância como número.
- Passar o estado como booleano: `True` ou `False`.
- Converter os textos dos CSVs antes de criar os objetos.
- Utilizar os métodos da rede para manter os dicionários consistentes.

A classe não verifica todos os tipos recebidos. A leitura dos CSVs deverá realizar as conversões e validações necessárias.

Desativar uma tubulação não remove seu cadastro nem sua adjacência. O método `vizinhos_ativos` ignora as conexões desativadas.

### Exemplo de uso

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
# Esperado: [("A", 2.0)]

cenario = rede.copiar()
cenario.alterar_estado("T1", False)

print(cenario.vizinhos_ativos("R"))
# Esperado: []

print(rede.vizinhos_ativos("R"))
# Esperado: [("A", 2.0)]
```

Esse exemplo também serve para verificar se a cópia é independente.

## 7. Base de dados R-9

A base escolhida é a **R-9**, disponibilizada no Mendeley Data.

- Fonte: https://data.mendeley.com/datasets/zyg68ck8xc/1
- DOI: https://doi.org/10.17632/zyg68ck8xc.1
- Arquivo utilizado: `R9_water_distribution_network_input_data.xlsx`

A referência completa e a licença da fonte deverão ser registradas na documentação dos dados e no relatório.

### Preparação dos dados

O script `scripts/preparar_r9_dataset.py` lê a planilha original e gera:

- `dados/nos.csv`
- `dados/tubulacoes.csv`

A preparação produziu:

- **62 nós**
- **72 tubulações**

Adaptações realizadas:

- Identificação do reservatório como `"R"`.
- Padronização dos identificadores dos nós como strings.
- Identificação das tubulações com o prefixo `"T"`.
- Conversão das distâncias de metros para quilômetros.
- Definição inicial das tubulações como ativas.

Os dados originais devem ser preservados para permitir conferir e reproduzir a conversão.

A conversão da planilha para CSV é uma etapa de preparação. O carregamento desses CSVs em objetos da classe `Rede` será feito separadamente em `servicos/leitura_csv.py`.

### Formato de nos.csv

Cabeçalho:

```csv
id,nome,tipo
```

### Formato de tubulacoes.csv

Cabeçalho:

```csv
id,origem,destino,distancia_km,ativa
```

### Regras de leitura

- Codificação UTF-8.
- Vírgula como separador.
- Ponto como separador decimal.
- Identificadores mantidos como strings.
- `distancia_km` convertida para número e atribuída a `distancia`.
- Textos `true` e `false` convertidos para `True` e `False`.
- Valores de estado diferentes dos esperados devem ser rejeitados.

Não utilizar `bool(texto)` para converter o estado: `bool("false")` também resulta em `True`, pois a string não está vazia.

A base preparada não fornece coordenadas para o desenho da aplicação. A visualização deverá ser esquemática ou utilizar posições definidas separadamente, sem apresentá-las como localização geográfica real.

## 8. Rede pequena para testes

Além da R-9, manteremos uma rede fictícia para testes fáceis de conferir manualmente.

Ela não substitui os CSVs da R-9.

### Nós

| ID | Função |
|---|---|
| R | Reservatório |
| A | Estação de bombeamento |
| B e C | Pontos intermediários |
| D, E, F e G | Setores de distribuição |

### Tubulações

| Conexão | Distância |
|---|---|
| R–A | 2 km |
| A–B | 2 km |
| A–C | 3 km |
| B–D | 2 km |
| B–E | 5 km |
| C–D | 6 km |
| C–E | 4 km |
| D–F | 2 km |
| E–F | 3 km |
| F–G | 2 km |

Total: **8 nós e 10 tubulações**.

### Resultados esperados

Cada cenário deve começar com a rede original, sem acumular falhas.

| Cenário | Resultado esperado |
|---|---|
| Rede original | Todos os nós alcançáveis a partir de R |
| Caminho mínimo R → G | R–A–B–D–F–G, com 10 km |
| Interrupção de B–D | Todos alcançáveis; menor distância R → G de 14 km |
| Interrupção de R–A | Apenas R alcançável a partir de R |
| Interrupção de F–G | G inacessível a partir de R |
| Pontes na rede original | R–A e F–G |

Sem B–D, existem duas rotas mínimas de 14 km:

- R–A–B–E–F–G
- R–A–C–E–F–G

Os testes devem aceitar qualquer uma dessas rotas.

Os IDs usados para identificar tubulações devem corresponder aos cadastrados na rede de teste. Uma conexão B–D não necessariamente possui o identificador `"B-D"`.

## 9. Algoritmos e integração

### Algoritmos planejados

| Algoritmo | Finalidade | Complexidade prevista |
|---|---|---|
| BFS | Encontrar os nós alcançáveis a partir da origem | O(V + E) |
| Dijkstra com fila de prioridade | Encontrar o caminho de menor distância | O((V + E) log V) |
| Tarjan para pontes | Identificar arestas cuja remoção aumenta o número de componentes | O(V + E) |

`V` representa a quantidade de vértices e `E`, a quantidade de arestas.

Todos os algoritmos devem considerar somente tubulações ativas.

A identificação de pontes deve percorrer todas as componentes, inclusive quando a rede já estiver desconectada.

### Contrato disponível da Rede

Os algoritmos podem utilizar:

```python
# Percorrer os identificadores dos nós
for identificador in rede.vertices:
    ...

# Percorrer os vizinhos ligados por tubulações ativas
for vizinho, distancia in rede.vizinhos_ativos(origem):
    ...

# Consultar o ID da tubulação entre dois nós adjacentes
id_tubulacao = rede.adjacencia[origem][destino]
```

O retorno de `vizinhos_ativos` contém **dois valores por item**: vizinho e distância.

### Contratos propostos para os demais módulos

Confirmar estes contratos com os responsáveis antes da integração.

| Função | Retorno proposto |
|---|---|
| `bfs(rede, origem)` | Conjunto dos IDs alcançáveis, incluindo a origem |
| `dijkstra(rede, origem, destino)` | Tupla `(caminho, distancia)` |
| `encontrar_pontes(rede)` | Conjunto dos IDs das tubulações críticas |
| `simular_falha(rede, origem, destino, tubulacao_id)` | Resultado organizado da comparação; estrutura a definir |

Para Dijkstra, a proposta é:

- Caminho encontrado: `(["R", "A"], 2.0)`.
- Destino inacessível: `([], None)`.
- Origem igual ao destino: `(["R"], 0)`.

Nó inexistente deve ser tratado como entrada inválida, diferente de um nó existente sem caminho até a origem.

### Como trabalhar em paralelo

1. Usar a interface da classe `Rede` como referência compartilhada.
2. Desenvolver os algoritmos com a rede pequena.
3. Desenvolver a interface com respostas provisórias claramente identificadas.
4. Implementar a simulação usando os contratos combinados.
5. Substituir as respostas provisórias pelos algoritmos reais.
6. Executar os testes de integração.

Não mudar nomes, argumentos ou retornos compartilhados sem avisar os colegas.

Os algoritmos de consulta não devem modificar a rede recebida. A simulação deve utilizar `rede.copiar()` para aplicar a falha.

Se o destino ficar inacessível, a interface deve mostrar essa condição. Não calcular uma diferença numérica envolvendo uma distância `None`.

## 10. Funcionalidades planejadas

- Visualização da rede.
- Seleção de origem e destino.
- Seleção de uma tubulação para interrupção.
- Identificação dos pontos alcançáveis e inacessíveis.
- Cálculo do caminho mínimo e de sua distância.
- Destaque das pontes.
- Comparação antes e depois da falha.
- Restauração do cenário para uma nova simulação.

A interface deve deixar claro que os resultados representam conectividade e distância, não uma simulação hidráulica.

## 11. Preparar o ambiente

Executar os comandos no Ubuntu ou WSL, dentro da pasta raiz do repositório.

### Criar o ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se faltar suporte a `venv`, instalar o pacote correspondente à versão do Python utilizada e repetir a criação do ambiente.

Ao abrir outro terminal, ativar novamente:

```bash
source .venv/bin/activate
```

### Instalar as dependências

Quando o `requirements.txt` estiver preenchido:

```bash
python -m pip install -r requirements.txt
```

Para executar apenas a preparação da planilha, a dependência externa necessária é:

```bash
python -m pip install openpyxl
```

O grupo deverá registrar no `requirements.txt` as dependências e versões efetivamente utilizadas.

As classes dos modelos não precisam de bibliotecas externas.

### Gerar os CSVs

Com a planilha original no local esperado pelo script:

```bash
python scripts/preparar_r9_dataset.py
```

Resultado esperado para a base utilizada:

```text
nos.csv criado com 62 nós.
tubulacoes.csv criado com 72 tubulações.
```

A preparação escreve os CSVs de saída. Evitar alterações manuais nesses arquivos que possam ser perdidas ao executar o script novamente.

### Executar a interface

Quando `app.py` estiver implementado e Streamlit instalado:

```bash
python -m streamlit run app.py
```

### Executar os testes

Se o grupo utilizar `unittest`, executar na raiz:

```bash
python -m unittest discover -s testes -v
```

Esse comando depende da implementação dos testes. Uma execução com zero testes não comprova o funcionamento do projeto.

## 12. Planejamento de testes

### Estrutura da rede

- Cadastro de nós e tubulações válidos.
- Rejeição de identificadores duplicados.
- Rejeição de origem ou destino inexistente.
- Rejeição de laços.
- Rejeição de distâncias menores ou iguais a zero.
- Rejeição de conexões duplicadas, inclusive invertidas.
- Consulta de vizinhos nos dois sentidos.
- Exclusão das conexões inativas da consulta.
- Ativação e desativação de tubulações.
- Cópia de uma rede vazia.
- Cópia de todos os nós e tubulações.
- Alteração da cópia sem modificar a original.

### Leitura dos CSVs

- Conferência dos cabeçalhos obrigatórios.
- Conversão de distâncias e estados.
- Rejeição de campos obrigatórios vazios e valores inválidos.
- Identificação de referências a nós inexistentes.
- Carregamento dos 62 nós e das 72 tubulações da R-9.

### Algoritmos e integração

- Resultados da rede pequena.
- Origem igual ao destino.
- Destino inacessível.
- Rotas mínimas empatadas.
- Redes com componentes desconectadas.
- Comparação sem alterar a rede original.
- Restauração do cenário.
- Exibição coerente dos resultados na interface.

## 13. Andamento

### Estrutura e preparação dos dados

- [x] Escolha da base R-9.
- [x] Preparação dos CSVs.
- [x] Implementação das classes `No` e `Tubulacao`.
- [x] Implementação dos métodos da classe `Rede`.
- [ ] Testes automatizados da estrutura.
- [ ] Carregamento dos CSVs em uma instância de `Rede`.
- [ ] UML atualizado.

## 14. Padrão de desenvolvimento e Git

### Código

- Utilizar nomes em português.
- Usar `snake_case` em funções, variáveis e arquivos.
- Usar nomes de classes como `No`, `Tubulacao` e `Rede`.
- Evitar acentos nos identificadores do código.
- Usar quatro espaços por nível de indentação.
- Escrever comentários quando ajudarem a explicar uma decisão.

### Colaboração

- Trabalhar no repositório compartilhado.
- Criar uma branch por funcionalidade.
- Fazer commits individuais.
- Abrir pull requests para revisão.
- Integrar as mudanças progressivamente.
- Atualizar a documentação quando um contrato mudar.

Sugestões de branches:

| Parte | Branch |
|---|---|
| Estrutura e dados | `feat/estrutura-rede` |
| BFS e pontes | `feat/bfs-pontes` |
| Dijkstra | `feat/dijkstra` |
| Interface | `feat/interface` |
| Simulação | `feat/simulacao` |

Exemplos de commits:

```text
feat: implementa modelos da rede e operações de nós e tubulações
feat: adiciona leitura dos arquivos CSV
test: verifica independência da cópia da rede
docs: atualiza instruções de integração no README
```

Não enviar o ambiente virtual ou caches ao repositório.

Conteúdo sugerido para `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
```

Preservar a autoria dos commits, pois as contribuições individuais serão avaliadas.

## 15. Cronograma interno

| Período de 2026 | Meta |
|---|---|
| 04 a 07/11 | Planejamento, modelagem, contratos e dados |
| 08 a 12/11 | Implementação e testes dos módulos |
| 13 a 16/11 | Integração dos algoritmos, simulação e interface |
| 17 a 19/11 | Testes completos, desempenho e relatório |
| 20 a 21/11 | Revisão, slides, vídeo e ensaio |
| 22/11 | Entrega prevista |

As datas são metas internas. Confirmar o prazo oficial e as instruções da tarefa no Canvas.

## 16. Entrega acadêmica

Checklist para revisão final:

- [ ] Aplicação funcional com interface gráfica.
- [ ] Estrutura de grafo e algoritmos implementados pelo grupo.
- [ ] Testes e resultados documentados.
- [ ] Origem dos dados e adaptações explicadas.
- [ ] Limitações da modelagem registradas.
- [ ] UML de classes e casos de uso atualizados.
- [ ] Avaliação de desempenho.
- [ ] Histórico Git com contribuições individuais.
- [ ] Relatório de 12 a 15 páginas em LaTeX no template SBC.
- [ ] Contribuições de cada integrante descritas.
- [ ] Apresentação presencial de 10 minutos.
- [ ] Vídeo de demonstração de 12 a 18 minutos.
- [ ] Participação dos cinco integrantes nas apresentações.
- [ ] ZIP com código-fonte, fonte `.tex`, PDF do relatório e arquivos necessários.
- [ ] Forma de envio dos demais materiais confirmada no Canvas.
- [ ] Entrega individual realizada por cada integrante.
