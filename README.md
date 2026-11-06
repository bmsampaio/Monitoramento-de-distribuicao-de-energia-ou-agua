# Monitoramento de redes de distribuição de água

Projeto da disciplina de **Teoria dos Grafos**, desenvolvido por um grupo de cinco integrantes.

**Tema escolhido:** Tema 4 — Monitoramento de distribuição de energia ou água.  
**Aplicação:** análise de uma rede de distribuição de água.  
**Nome provisório:** Sistema Inteligente de Monitoramento e Análise de Falhas em Redes de Distribuição de Água.

> **Situação inicial:** este README descreve o que vamos desenvolver. Criar as pastas e os arquivos vazios ainda não significa que a aplicação está funcionando. Atualizaremos as instruções conforme cada parte ficar pronta.

## 1. O que vamos construir?

Vamos criar um programa que mostra uma rede de água e permite simular a interrupção de uma tubulação.

O usuário poderá escolher uma origem e um destino, visualizar o menor caminho entre eles e verificar o que acontece quando uma conexão é desativada.

O sistema deverá responder:

- Quais pontos continuam conectados ao reservatório?
- Quais pontos ficam inacessíveis depois de uma falha?
- Existe outro caminho até o destino?
- Qual é o caminho com a menor distância?
- Quais tubulações são críticas para a conectividade da rede?

**Exemplo:** na rede inicial, o menor caminho entre R e G tem 10 km. Se a tubulação B–D for interrompida, ainda existe conexão, mas a menor distância passa a ser 14 km.

## 2. Como vamos representar a rede?

Usaremos um **grafo não direcionado e ponderado**:

| Elemento | Representação no projeto |
|---|---|
| Vértice ou nó | Reservatório, estação, ponto intermediário ou setor |
| Aresta | Tubulação entre dois pontos |
| Peso da aresta | Distância da tubulação em quilômetros |
| Estado da aresta | Ativa ou inativa |

O grafo será guardado em uma **lista de adjacência implementada com dicionários Python**. Essa estrutura informa quais pontos estão ligados a cada ponto da rede.

Como o grafo não é direcionado, a conexão R–A também permite consultar A–R. Isso representa uma ligação estrutural entre os pontos.

### Limites do projeto

O programa **não fará simulação hidráulica**: não calculará pressão, vazão ou atendimento da demanda. Um caminho no grafo não garante que o abastecimento real seja possível.

A capacidade nominal será apenas uma informação cadastrada, sem interferir no cálculo das rotas. Na rede fictícia, ela ainda não foi informada.

A primeira versão trabalhará com **uma falha por comparação**, sempre em relação à rede carregada. Falhas acumuladas podem ser discutidas depois.

## 3. Tecnologias e algoritmos

| Recurso | Uso |
|---|---|
| Python 3 | Implementação do projeto |
| Streamlit | Interface gráfica |
| Matplotlib | Desenho da rede e destaque dos resultados |
| Git | Histórico e colaboração |
| CSV | Arquivos de entrada |
| LaTeX | Relatório final no template SBC |

| Algoritmo | Pergunta que responde | Responsável |
|---|---|---|
| BFS — busca em largura | Quais pontos estão conectados à origem? | Integrante 2 |
| Dijkstra | Qual é o caminho de menor distância? | Integrante 3 |
| Tarjan para pontes | Quais conexões, se removidas, separam uma componente da rede? | Integrante 2 |

Os algoritmos e a estrutura do grafo serão implementados pelo grupo. **Não usar NetworkX ou bibliotecas equivalentes para criar ou processar o grafo.** O enunciado permite esse tipo de biblioteca apenas para comparação de desempenho; ela não fará parte do funcionamento da aplicação.

Módulos gerais do Python, como `csv`, `collections`, `heapq` e `copy`, podem apoiar a implementação. Matplotlib será usado para desenhar, não para calcular os algoritmos.

## 4. Quem faz o quê?

| Integrante | Nome | Responsabilidade principal |
|---|---|---|
| 1 | Bárbara | Estrutura da rede, leitura de CSV e dados iniciais |
| 2 | A preencher | BFS e identificação de pontes |
| 3 | A preencher | Dijkstra e avaliação de desempenho |
| 4 | A preencher | Interface Streamlit e desenho com Matplotlib |
| 5 | A preencher | Simulação de falhas e integração |

### Integrante 1 — estrutura e dados

- Criar as classes `No`, `Tubulacao` e `Rede`.
- Adicionar pontos e conexões à rede.
- Permitir consultar vizinhos ativos, ativar/desativar tubulações e copiar a rede.
- Montar primeiro a rede de exemplo diretamente em Python.
- Criar os CSVs e implementar sua leitura com validação.
- Produzir o UML de classes e documentar a modelagem.
- Testar a estrutura e pesquisar uma base pública com apoio do integrante 3.

**Primeira entrega:** classes básicas e rede de exemplo para liberar o desenvolvimento dos algoritmos.

### Integrante 2 — conectividade e pontes

- Implementar BFS e Tarjan para pontes.
- Considerar apenas tubulações ativas.
- Testar redes conectadas, desconexas, ciclos e árvores.
- Documentar funcionamento, complexidades e resultados.

**Primeira entrega:** BFS funcionando na rede inicial; depois, busca de pontes.

### Integrante 3 — caminhos mínimos e desempenho

- Implementar Dijkstra usando distância como peso.
- Tratar destino inacessível, origem igual ao destino e rotas empatadas.
- Criar testes de caminhos mínimos.
- Organizar medições em redes maiores, com apoio dos outros autores.
- Documentar o algoritmo e os resultados medidos.

**Primeira entrega:** cálculo de R até G com resultado de 10 km na rede original.

### Integrante 4 — interface e visualização

- Criar a tela, os seletores e os botões.
- Desenhar pontos, tubulações, rotas, pontes e falhas.
- Exibir resultados antes e depois da interrupção.
- Ligar os controles ao serviço de simulação.
- Produzir casos de uso, capturas de tela e documentação da interface.

**Primeira entrega:** tela com a rede e respostas fixas de exemplo, usadas temporariamente durante o desenvolvimento.

### Integrante 5 — simulação e integração

- Criar o serviço que compara a rede antes e depois da falha.
- Trabalhar com uma cópia independente para preservar a rede original.
- Chamar BFS, Dijkstra e a identificação de pontes.
- Calcular os novos pontos inacessíveis e a mudança de distância quando comparável.
- Coordenar testes de integração e instruções de execução.
- Documentar os cenários e organizar o roteiro conjunto de demonstração.

**Primeira entrega:** estrutura da simulação com funções provisórias; depois, conexão com os algoritmos reais.

### Responsabilidades de todos

Cada integrante deve planejar, implementar, testar e documentar sua parte, fazer commits próprios, revisar o trabalho de um colega e participar das apresentações. O relatório não ficará sob responsabilidade de uma única pessoa.

Quem escreveu um módulo continua responsável por corrigir seus problemas durante a integração.

## 5. Estrutura do repositório

```text
monitoramento_agua/
├── app.py
├── visualizacao.py
├── modelos/
│   ├── __init__.py
│   ├── no.py
│   ├── tubulacao.py
│   └── rede.py
├── algoritmos/
│   ├── __init__.py
│   ├── bfs.py
│   ├── dijkstra.py
│   └── pontes.py
├── servicos/
│   ├── __init__.py
│   ├── leitura_csv.py
│   └── simulacao.py
├── dados/
│   ├── nos.csv
│   └── tubulacoes.csv
├── exemplos/
│   ├── __init__.py
│   └── rede_exemplo.py
├── testes/
│   ├── __init__.py
│   ├── test_rede.py
│   ├── test_leitura_csv.py
│   ├── test_bfs.py
│   ├── test_dijkstra.py
│   ├── test_pontes.py
│   └── test_simulacao.py
├── docs/
│   ├── combinados.md
│   ├── diagramas/
│   ├── imagens/
│   └── relatorio/
├── .gitignore
├── requirements.txt
└── README.md
```

| Local | Conteúdo |
|---|---|
| `modelos/` | Classes que guardam e organizam os dados da rede |
| `algoritmos/` | Implementações de BFS, Dijkstra e pontes |
| `servicos/` | Leitura dos dados e comparação de cenários |
| `dados/` | CSVs utilizados pelo programa |
| `exemplos/` | Rede criada em Python para começar sem depender do CSV |
| `testes/` | Verificações de cada módulo e da integração |
| `docs/combinados.md` | Nomes das funções, entradas, saídas e decisões compartilhadas |
| `docs/diagramas/` | UML e demais diagramas |
| `docs/imagens/` | Capturas reais da aplicação |
| `docs/relatorio/` | Fontes LaTeX e arquivos do relatório |
| `app.py` | Interface e interação do usuário |
| `visualizacao.py` | Funções de desenho da rede |
| `requirements.txt` | Dependências externas, preenchidas conforme forem utilizadas |

Os arquivos `__init__.py` podem começar vazios. Eles permitem organizar essas pastas como pacotes Python.

**Pastas vazias não são registradas pelo Git.** Quando necessário, colocar um arquivo `.gitkeep` nelas ou aguardar a inclusão do primeiro documento.

## 6. Como trabalhar em paralelo

Não precisamos esperar uma pessoa terminar toda a parte dela para começar as outras. Precisamos apenas definir o formato compartilhado dos dados.

1. O grupo combina as funções e seus retornos em `docs/combinados.md`.
2. A integrante 1 entrega uma rede pequena com consulta de vizinhos.
3. Os integrantes 2 e 3 desenvolvem e testam seus algoritmos nessa rede.
4. O integrante 4 cria a tela com resultados de exemplo.
5. O integrante 5 organiza a comparação com funções provisórias.
6. O grupo substitui as respostas de exemplo pelos módulos reais e testa o fluxo completo.

**Não mudar nomes ou retornos de funções compartilhadas sem avisar os colegas que as utilizam.**

### Proposta inicial de funções — confirmar em grupo

Estas assinaturas orientam o desenvolvimento; não indicam que as funções já existem.

| Função ou método | Resultado esperado |
|---|---|
| `rede.adicionar_no(no)` | Cadastra um ponto |
| `rede.adicionar_tubulacao(tubulacao)` | Cadastra a ligação nos dois sentidos |
| `rede.vizinhos_ativos(id_no)` | Retorna vizinho, distância e ID da tubulação |
| `rede.definir_estado(id_tubulacao, ativa)` | Ativa ou desativa a conexão |
| `rede.copiar()` | Retorna uma cópia independente |
| `bfs(rede, origem)` | Retorna os IDs alcançáveis |
| `dijkstra(rede, origem, destino)` | Retorna caminho e distância total |
| `encontrar_pontes(rede)` | Retorna IDs das tubulações críticas |
| `simular_falha(rede, origem, destino, tubulacao_id)` | Retorna a comparação antes/depois |

Antes da integração, registrar os tipos exatos de retorno e como representar erros e ausência de caminho. Os algoritmos de consulta não devem alterar a rede recebida.

## 7. Dados e rede inicial

### Pontos

| ID | Função |
|---|---|
| R | Reservatório principal |
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

Total: **8 vértices e 10 arestas**, inicialmente ativas.

### Formato proposto dos CSVs

`dados/nos.csv`:

```csv
id,nome,tipo
R,Reservatório principal,reservatorio
A,Estação de bombeamento,bombeamento
```

`dados/tubulacoes.csv`:

```csv
id,origem,destino,distancia_km,capacidade_nominal,ativa
T01,R,A,2,,true
```

Esses trechos mostram apenas o formato; não são a rede completa. Usar UTF-8, vírgula como separador e ponto para casas decimais. Capacidade vazia significa “não informada”; o leitor deverá converter o texto `true` ou `false` para o estado correspondente.

Na primeira versão, rejeitar IDs duplicados, referências a pontos inexistentes, distâncias negativas, laços e conexões duplicadas entre o mesmo par de pontos, mesmo no sentido inverso. Demais regras serão registradas em `docs/combinados.md`.

## 8. Resultados esperados nos testes

Cada cenário abaixo começa na rede original, sem acumular a falha anterior.

| Cenário | Resultado esperado |
|---|---|
| Rede original | Todos os oito pontos alcançáveis a partir de R |
| Menor caminho R→G | R–A–B–D–F–G, com 10 km |
| B–D interrompida | Todos continuam alcançáveis; menor distância R→G de 14 km |
| R–A interrompida | Só R é alcançável a partir de R; os outros sete pontos ficam inacessíveis |
| F–G interrompida | G fica inacessível a partir de R |
| Pontes na rede original | R–A e F–G |
| Rede restaurada | Estados iniciais recuperados e rota R→G de 10 km |

Sem B–D, há duas rotas mínimas de 14 km: **R–A–B–E–F–G** e **R–A–C–E–F–G**. Os testes devem aceitar ambas.

Também testar cópia independente, dados inválidos, origem igual ao destino, destino sem caminho e redes desconexas.

## 9. Preparar o ambiente — Ubuntu ou WSL

Executar os comandos no terminal do Linux, dentro da pasta raiz do repositório. Se já houver um repositório compartilhado, usar a cópia clonada dele, evitando criar outro projeto separado.

### Verificar o Python

```bash
python3 --version
```

O grupo deve combinar uma versão de Python 3 e registrar aqui a versão efetivamente testada. Ainda não foi definida uma versão mínima do projeto.

### Criar e ativar o ambiente virtual

O ambiente virtual separa as bibliotecas deste projeto das de outros projetos.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Se o Ubuntu informar que falta suporte a `venv`, instalar o pacote correspondente ao Python utilizado. Para o Python padrão do Ubuntu, normalmente:

```bash
sudo apt update
sudo apt install python3-venv
```

Depois, repetir a criação do ambiente. Não é necessário instalar bibliotecas externas para começar as classes da rede.

### Instalar as dependências cadastradas

Quando `requirements.txt` estiver preenchido:

```bash
python -m pip install -r requirements.txt
```

Um arquivo vazio não instala Streamlit, Matplotlib ou qualquer outra biblioteca. O grupo deve adicionar as dependências e versões testadas conforme forem usadas.

Ao abrir outro terminal, ativar novamente o ambiente com `source .venv/bin/activate`. Para sair dele, usar `deactivate`.

### Executar — conforme as partes forem implementadas

| Comando, na raiz | Quando utilizar |
|---|---|
| `python -m exemplos.rede_exemplo` | Quando esse módulo tiver uma rotina que monta e exibe a rede |
| `python -m unittest discover -s testes -v` | Se os testes forem escritos usando `unittest` |
| `python -m streamlit run app.py` | Quando a interface estiver implementada e Streamlit instalado |

Arquivos vazios podem não produzir saída. Uma execução com **zero testes** não comprova que o código está correto. Se o grupo escolher outro framework de testes, atualizar o comando neste README.

## 10. Git e colaboração

- Manter uma branch principal com o código integrado.
- Criar uma branch para cada funcionalidade.
- Fazer commits individuais com mensagens que expliquem a mudança.
- Abrir um pull request e pedir revisão de um colega antes de integrar.
- Testar novamente quando juntar módulos.

Sugestões de branches:

| Parte | Branch |
|---|---|
| Estrutura e dados | `feat/estrutura-rede` |
| BFS e pontes | `feat/bfs-pontes` |
| Dijkstra | `feat/dijkstra` |
| Interface | `feat/interface` |
| Simulação | `feat/simulacao` |

Exemplo de mensagem de commit: `Implementa consulta de vizinhos ativos da rede`.

Não enviar o ambiente virtual, caches ou arquivos temporários. Conteúdo inicial sugerido para `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
```

Preservar o histórico de autoria: os commits individuais serão avaliados pelo professor.

## 11. Organização das próximas entregas

| Período interno | Meta |
|---|---|
| 04 a 07/11/2026 | Divisão, modelagem, UML, formato dos dados e rede mínima |
| 08 a 12/11/2026 | Implementação e testes separados dos módulos |
| 13 a 16/11/2026 | Integração dos algoritmos, simulação e tela |
| 17 a 19/11/2026 | Testes completos, desempenho e relatório |
| 20 a 21/11/2026 | Revisão, slides, vídeo e ensaio |
| 22/11/2026 | Entrega prevista |

Essas datas são metas internas. O enunciado informa **22/11** e determina entrega até **23:59 conforme a tarefa do Canvas**. Confirmar o ano, o prazo e os canais de envio no Canvas. As três etapas têm a mesma data final oficial.

## 12. Checklist final do grupo

- [ ] Estrutura própria de grafo funcionando.
- [ ] BFS, Dijkstra e pontes implementados e testados.
- [ ] Interface mostrando rede, caminhos, falhas e regiões afetadas.
- [ ] Comparação e restauração funcionando.
- [ ] UML de classes e casos de uso atualizados.
- [ ] Pesquisa de base pública registrada, incluindo origem e adaptações.
- [ ] Resultados e medições de desempenho documentados.
- [ ] README atualizado com instruções realmente testadas.
- [ ] Relatório de 12 a 15 páginas em LaTeX no template oficial SBC.
- [ ] Contribuição de cada integrante descrita no relatório.
- [ ] Slides e apresentação presencial de 10 minutos.
- [ ] Vídeo de 12 a 18 minutos demonstrando as funcionalidades de cada integrante.
- [ ] Participação dos cinco nas duas apresentações.
- [ ] ZIP com código-fonte, fonte `.tex`, PDF do relatório e arquivos necessários para execução e compilação.
- [ ] Forma de envio do vídeo, slides e acesso ao Git confirmada no Canvas.
- [ ] Cada integrante realizou sua própria entrega e guardou o comprovante.

> O enunciado prevê nota zero por falta de itens obrigatórios ou ausência de entrega individual. Conferir todos os itens antes de enviar.

## 13. O que ainda precisamos combinar

- Preencher os nomes dos integrantes 2 a 5.
- Definir a versão de Python utilizada pelo grupo.
- Confirmar os formatos de entrada e saída das funções.
- Definir a ferramenta de testes e as dependências externas.
- Escolher a base pública para pesquisa e testes maiores.
- Confirmar prazo e instruções no Canvas.

**Fonte das exigências acadêmicas:** enunciado `TP.pdf`, fornecido pelo professor. Em caso de divergência, seguir o enunciado e as orientações oficiais da disciplina.
