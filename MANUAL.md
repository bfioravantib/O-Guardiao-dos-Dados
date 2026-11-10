# Manual técnico — O Guardião dos Dados

**Autor:** Bruno Fioravanti

Este manual explica como o projeto está organizado, o que faz cada arquivo e cada função, e — principalmente —
**onde mexer quando você quiser mudar alguma coisa**. Se estiver com pressa, vá direto à seção
[11. Onde alterar cada coisa](#11-onde-alterar-cada-coisa).

> Os números de linha citados valem para a versão atual do código. Se o arquivo mudar, procure pelo nome da
> função ou da variável (Ctrl+F), que continua o mesmo.

---

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Tecnologias usadas](#2-tecnologias-usadas)
3. [Estrutura de pastas](#3-estrutura-de-pastas)
4. [Configurações e variáveis de ambiente](#4-configurações-e-variáveis-de-ambiente)
5. [Banco de dados](#5-banco-de-dados)
6. [Páginas e endereços (rotas)](#6-páginas-e-endereços-rotas)
7. [Funções do Model (dados)](#7-funções-do-model-dados)
8. [Funções do Controller (rotas, gráficos e PDF)](#8-funções-do-controller-rotas-gráficos-e-pdf)
9. [Templates (View/Página)](#9-templates-viewpágina)
10. [Estilo visual (View/Estilo/style.css)](#10-estilo-visual-viewestilostylecss)
11. [Onde alterar cada coisa](#11-onde-alterar-cada-coisa)
12. [Cuidados e armadilhas](#12-cuidados-e-armadilhas)

---

## 1. Visão geral

É um quiz web de cibersegurança e LGPD com tema medieval. O participante informa o nome, responde às
"provações" (perguntas de 5 alternativas), vê o comentário do Guardião após cada resposta e recebe um título
no final. Uma área administrativa protegida por PIN mostra estatísticas, o histórico de jornadas, gráficos,
relatórios em PDF e permite cadastrar perguntas.

**Como uma jornada acontece, do clique ao banco:**

```
Menu (/)  ──nome──▶  /jogo/  ──▶  /jogo/pergunta  ⇄  /jogo/responder  ──▶  /jogo/proxima
                                         │                                       │
                                         └──── (repete para cada pergunta) ◀─────┘
                                                                                 │ última pergunta
                                                                                 ▼
                                             grava partida + respostas no banco ──▶ /jogo/resultado
```

- Enquanto o jogo acontece, o andamento (perguntas, posição atual, respostas dadas) fica **na sessão** do
  navegador (um cookie assinado). Nada vai para o banco no meio do caminho.
- Só quando a última pergunta é concluída a jornada é gravada (tabela `partidas`) junto com cada resposta
  (tabela `respostas`). É dessas duas tabelas que saem todas as estatísticas, gráficos e PDFs.

O código segue o padrão **MVC**:

| Camada         | Pasta         | Responsabilidade                                                    |
|----------------|---------------|---------------------------------------------------------------------|
| **Model**      | `Model/`      | Configuração, conexão com o banco e todas as consultas SQL          |
| **View**       | `View/`       | O que aparece na tela: HTML (templates Jinja) e CSS                 |
| **Controller** | `Controller/` | Recebe cada requisição, chama o Model e escolhe qual View mostrar   |

---

## 2. Tecnologias usadas

| Tecnologia | Onde aparece | O que constrói no projeto |
|---|---|---|
| **Python 3.12** | todo o back-end | Linguagem do servidor. |
| **Flask** (`requirements.txt`) | `app.py`, `Controller/` | Framework web: recebe as requisições, define as rotas (URLs), cuida da sessão (cookie assinado) e renderiza os templates. Os *blueprints* (`menu`, `jogo`, `admin`) separam as rotas por assunto. |
| **Jinja2** (vem com o Flask) | `View/Página/*.html` | Linguagem dos templates: `{{ variavel }}` imprime valores, `{% if %}`/`{% for %}` controlam o HTML, `{% extends %}` herda o layout de `base.html` e `{% macro %}` cria "componentes" reutilizáveis (Guardião, gráficos). |
| **SQLite** (vem com o Python) | `Model/banco.py` | Banco local em arquivo (`quiz.db`), usado quando você roda no seu computador. Criado sozinho na primeira execução. |
| **PostgreSQL / Neon** + **psycopg** | `Model/banco.py` | Banco de produção no Vercel. O Neon é um PostgreSQL na nuvem; o psycopg é a biblioteca Python que conversa com ele. Usado sempre que a variável `DATABASE_URL` existir. |
| **ReportLab** | `Controller/relatorio_pdf.py` | Gera os relatórios em PDF (textos, tabelas, gráficos de pizza e de barras) diretamente no servidor. |
| **SVG** (desenho vetorial no HTML) | `_guardiao.html`, `_graficos.html`, `graficos.py` | O personagem Guardião, o título medieval, o cenário do menu e os gráficos de pizza da tela são desenhados em SVG — não há imagens nem bibliotecas de gráficos JavaScript. |
| **CSS** | `View/Estilo/style.css` | Todo o visual: cores, tema pergaminho, botões, layout para celular, barras dos gráficos de participantes. |
| **JavaScript** (pequeno, embutido) | `jogo.html`, `admin_estatisticas.html` | Só dois detalhes: atalhos de teclado A–E/1–5 no jogo e a caixa "marcar todas" nas estatísticas. O site funciona sem JavaScript. |
| **Google Fonts** (Cinzel / Cinzel Decorative) | `base.html` | Fontes medievais dos títulos. |
| **zoneinfo + tzdata** | `Model/config.py` | Fuso horário: grava e mostra as datas no horário de Brasília mesmo com o servidor do Vercel em UTC. O `tzdata` fornece a tabela de fusos no Windows. |
| **Vercel** | `app.py` (variável `app`) | Hospedagem. O Vercel procura uma variável `app` no `app.py` e a executa como função *serverless*. |

---

## 3. Estrutura de pastas

```
Urna-da-Justi-a/
├── app.py                    ← ponto de entrada: cria o app Flask (local e Vercel)
├── requirements.txt          ← bibliotecas Python necessárias
├── README.md                 ← como executar e publicar
├── MANUAL.md                 ← este manual
├── quiz.db                   ← banco SQLite local (criado sozinho; não vai para o GitHub)
│
├── Model/
│   ├── config.py             ← TODAS as configurações (PIN, banco, fuso, letras…)
│   ├── banco.py              ← conexão SQLite/PostgreSQL e criação das tabelas
│   ├── repositorio.py        ← todas as consultas: perguntas, partidas, estatísticas
│   └── perguntas_iniciais.py ← as 5 perguntas de exemplo
│
├── Controller/
│   ├── menu.py               ← tela inicial
│   ├── jogo.py               ← fluxo do quiz
│   ├── admin.py              ← área administrativa
│   ├── graficos.py           ← cálculo das fatias da pizza (SVG)
│   └── relatorio_pdf.py      ← geração dos PDFs
│
└── View/
    ├── Estilo/style.css      ← visual de todas as páginas (servido em /estilo/style.css)
    └── Página/               ← templates HTML
        ├── base.html                 ← layout comum a todas as páginas
        ├── menuprincipal.html        ← menu inicial
        ├── jogo.html                 ← tela de cada pergunta
        ├── resultado.html            ← fim da jornada
        ├── sem_perguntas.html        ← aviso quando não há perguntas
        ├── admin_login.html          ← pedido de PIN
        ├── admin.html                ← layout da área admin (abas)
        ├── admin_estatisticas.html   ← aba Estatísticas
        ├── admin_jornadas.html       ← aba Registro de Jornadas
        ├── admin_perguntas.html      ← aba Grimório de Perguntas (lista)
        ├── admin_form_pergunta.html  ← formulário de nova/editar pergunta
        ├── _guardiao.html            ← macros: personagem, cenário e título (SVG)
        └── _graficos.html            ← macros: pizza, barras e percentual
```

Arquivos que começam com `_` não são páginas: são bibliotecas de macros importadas por outras páginas.

---

## 4. Configurações e variáveis de ambiente

Tudo fica em [Model/config.py](Model/config.py). Várias configurações podem vir de **variáveis de ambiente**
(definidas no Vercel em *Settings → Environment Variables*). Quando a variável não existe, vale o valor padrão
escrito no código.

| Nome no código | Variável de ambiente | Padrão | Para que serve |
|---|---|---|---|
| [`PIN_ADMIN`](Model/config.py#L10) | `QUIZ_PIN_ADMIN` | `1234` (só para uso local) | PIN da área administrativa. |
| [`URL_BANCO`](Model/config.py#L14) | `DATABASE_URL` ou `POSTGRES_URL` | — | Endereço do PostgreSQL (Neon). Se existir, o app usa PostgreSQL; se não, SQLite. |
| [`CAMINHO_BANCO`](Model/config.py#L19) | `QUIZ_BANCO` | `quiz.db` na raiz (ou `/tmp/quiz.db` no Vercel) | Arquivo SQLite. Útil para testes com um banco separado. |
| [`FUSO`](Model/config.py#L22) | `QUIZ_FUSO` | `America/Sao_Paulo` | Fuso das datas gravadas e exibidas. |
| `SECRET_KEY` (em [app.py](app.py#L22)) | `QUIZ_SECRET_KEY` | aleatória a cada início | Assina o cookie da sessão. **No Vercel, defina-a**: sem ela, cada instância do servidor gera uma chave diferente e os jogadores perdem o progresso. |
| — | `VERCEL` | (o Vercel define sozinho) | Só serve para o SQLite cair em `/tmp`, a única pasta gravável no Vercel. |

Constantes que só existem no código (sem variável de ambiente):

| Nome | Valor | Para que serve |
|---|---|---|
| [`RAIZ`](Model/config.py#L6) | pasta do projeto | Base para achar `View/` e `quiz.db`. |
| [`LETRAS`](Model/config.py#L24) | `['A','B','C','D','E']` | Letras exibidas nas alternativas. |
| [`QTD_ALTERNATIVAS`](Model/config.py#L25) | `5` | Quantas alternativas o formulário de pergunta exige. |
| [`TAMANHO_MAXIMO_NOME`](Model/config.py#L28) | `40` | Limite do nome do participante (campo do menu e valor gravado). |

> **PIN em produção:** o PIN escrito em `config.py` vai para o GitHub junto com o código. Para o site
> publicado, prefira definir `QUIZ_PIN_ADMIN` no Vercel — a variável de ambiente sempre tem prioridade sobre
> o valor do código.

---

## 5. Banco de dados

O esquema está em [Model/banco.py](Model/banco.py#L24) (constante `ESQUEMA`). São três tabelas:

**`perguntas`** — o "grimório"

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id` | inteiro, automático | Identificador. |
| `enunciado` | texto | A pergunta. |
| `alternativas` | texto | Lista JSON com as 5 alternativas, ex.: `["...", "...", ...]`. |
| `correta` | inteiro | Índice da alternativa certa (0 = A, 1 = B … 4 = E). |
| `comentario` | texto | "Sabedoria do Guardião", exibida após responder. |

**`partidas`** — uma linha por jornada concluída

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id` | inteiro, automático | Identificador. |
| `data` | texto | Data/hora com fuso, ex.: `2026-11-10T11:46:13-03:00`. |
| `total` | inteiro | Quantas perguntas foram respondidas. |
| `acertos` | inteiro | Quantas acertou. |
| `participante` | texto ou vazio | Nome informado no menu (vazio nas jornadas anteriores a esse campo). |

**`respostas`** — uma linha por pergunta respondida em cada jornada

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id` | inteiro, automático | Identificador. |
| `partida_id` | inteiro | A jornada (apagar a jornada apaga suas respostas — *ON DELETE CASCADE*). |
| `pergunta_id` | inteiro | A pergunta respondida (sem vínculo obrigatório, para o histórico sobreviver à exclusão da pergunta). |
| `enunciado` | texto | Cópia do enunciado no momento da resposta. |
| `escolhida` | inteiro | Alternativa marcada (0–4). |
| `correta` | inteiro | Alternativa certa naquele momento (0–4). |

**Criação e atualização automáticas:** ao iniciar, `banco.inicializar()` cria as tabelas se não existirem
(e cadastra as perguntas de exemplo) e `_atualizar_esquema()` adiciona colunas novas em bancos antigos. Você
nunca precisa rodar SQL à mão — nem no `quiz.db`, nem no Neon.

**Ver os dados:** localmente, abra `quiz.db` com qualquer visualizador de SQLite (ex.: extensão *SQLite
Viewer* do VS Code). No Neon, use o *SQL Editor* do painel do Neon (acessível pela aba *Storage* do Vercel).

---

## 6. Páginas e endereços (rotas)

| Endereço | Método | Função | Template | O que faz |
|---|---|---|---|---|
| `/` | GET | [`menu.inicio`](Controller/menu.py#L11) | `menuprincipal.html` | Menu com o campo de nome e o botão "Iniciar Provação". |
| `/jogo/` | GET | [`jogo.iniciar`](Controller/jogo.py#L35) | — (redireciona) | Guarda o nome, monta a lista de perguntas (na ordem de cadastro) e começa a jornada. |
| `/jogo/pergunta` | GET | [`jogo.pergunta`](Controller/jogo.py#L50) | `jogo.html` | Mostra a pergunta atual (ou o feedback, se já respondida). |
| `/jogo/responder` | POST | [`jogo.responder`](Controller/jogo.py#L74) | — | Registra a alternativa clicada na sessão. |
| `/jogo/proxima` | POST | [`jogo.proxima`](Controller/jogo.py#L95) | — | Avança; na última pergunta grava a jornada no banco. |
| `/jogo/resultado` | GET | [`jogo.resultado`](Controller/jogo.py#L109) | `resultado.html` | Placar, título conquistado e resumo das respostas. |
| `/admin/login` | GET/POST | [`admin.login`](Controller/admin.py#L29) | `admin_login.html` | Pede o PIN. |
| `/admin/sair` | GET | [`admin.sair`](Controller/admin.py#L40) | — | Sai da área admin. |
| `/admin/` | GET | [`admin.inicio`](Controller/admin.py#L46) | — | Redireciona para Estatísticas. |
| `/admin/estatisticas` | GET | [`admin.estatisticas`](Controller/admin.py#L61) | `admin_estatisticas.html` | Acerto por pergunta; com `?graficos=1` mostra as pizzas; `?p=<id>` filtra perguntas. |
| `/admin/estatisticas/pdf` | GET | [`admin.estatisticas_pdf`](Controller/admin.py#L73) | — (PDF) | Baixa o relatório de estatísticas. |
| `/admin/jornadas` | GET | [`admin.jornadas`](Controller/admin.py#L82) | `admin_jornadas.html` | Indicadores, média por participante e lista de jornadas. |
| `/admin/jornadas/pdf` | GET | [`admin.jornadas_pdf`](Controller/admin.py#L96) | — (PDF) | Baixa o relatório de jornadas. |
| `/admin/jornadas/limpar` | POST | [`admin.limpar_jornadas`](Controller/admin.py#L105) | — | Apaga todo o histórico (jornadas e respostas). |
| `/admin/perguntas` | GET | [`admin.perguntas`](Controller/admin.py#L122) | `admin_perguntas.html` | Lista as perguntas. |
| `/admin/perguntas/nova` | GET/POST | [`admin.nova_pergunta`](Controller/admin.py#L157) | `admin_form_pergunta.html` | Cadastra pergunta. |
| `/admin/perguntas/<id>/editar` | GET/POST | [`admin.editar_pergunta`](Controller/admin.py#L169) | `admin_form_pergunta.html` | Edita pergunta. |
| `/admin/perguntas/<id>/excluir` | POST | [`admin.excluir_pergunta`](Controller/admin.py#L183) | — | Exclui pergunta (o histórico dela é mantido). |
| `/admin/perguntas/restaurar` | POST | [`admin.restaurar_perguntas`](Controller/admin.py#L189) | — | Troca todas as perguntas pelas 5 de exemplo. |
| `/estilo/style.css` | GET | (Flask) | — | Arquivo de estilo. |

Todas as rotas `/admin/...` exceto o login passam antes por [`exigir_acesso`](Controller/admin.py#L21), que
manda para o login quem não digitou o PIN.

---

## 7. Funções do Model (dados)

### [app.py](app.py)

| Função / item | O que faz |
|---|---|
| `criar_app()` | Cria o Flask apontando os templates para `View/Página` e o CSS para `View/Estilo` (servido em `/estilo`), define a chave da sessão, prepara o banco (`banco.inicializar`) e registra os três blueprints. |
| `app = criar_app()` | Instância usada pelo Vercel. **Não remova nem renomeie** — o Vercel procura exatamente `app`. |
| `if __name__ == '__main__'` | Só roda com `python app.py`: servidor local em `http://127.0.0.1:5000`, com modo debug (recarrega ao salvar arquivos). |

### [Model/banco.py](Model/banco.py) — conexão e esquema

| Função / item | O que faz |
|---|---|
| `USA_POSTGRES` | `True` quando há `DATABASE_URL`; decide qual banco usar em todo o resto do código. |
| `ESQUEMA` / `COLUNA_ID` | O SQL de criação das tabelas; `{ID}` vira o tipo de chave automática de cada banco. |
| `class Conexao` | Deixa SQLite e PostgreSQL com a mesma "cara": `execute`, `executemany`, `commit`, `close`. Converte o marcador `?` (SQLite) para `%s` (PostgreSQL), então as consultas são escritas uma vez só. |
| `conectar()` | Abre uma conexão nova (PostgreSQL com resultados em dicionário; SQLite com chaves estrangeiras ligadas). |
| `obter()` | Conexão da requisição atual: abre na primeira consulta e reaproveita até o fim da requisição. É o que o repositório usa. |
| `fechar()` | Fecha a conexão no fim de cada requisição (registrado em `app.py`). |
| `inserir_perguntas_iniciais(conexao)` | Grava as perguntas de `perguntas_iniciais.py`. |
| `_tabela_perguntas_existe(conexao)` | Diz se o banco já foi criado. |
| `_coluna_existe(conexao, tabela, coluna)` | Diz se uma coluna existe (usado nas atualizações de esquema). |
| `_atualizar_esquema(conexao)` | Ajusta bancos antigos — hoje adiciona `partidas.participante` se faltar. É aqui que entram futuras colunas novas. |
| `inicializar()` | Roda uma vez ao iniciar: cria tudo se for um banco novo e aplica `_atualizar_esquema`. No PostgreSQL usa uma trava (*advisory lock*) para duas instâncias do Vercel não cadastrarem as perguntas em dobro. |

### [Model/repositorio.py](Model/repositorio.py) — todas as consultas

*Datas e cálculo*

| Função | O que faz |
|---|---|
| `agora()` | Data/hora atual no fuso configurado. Usada ao gravar jornadas e no rodapé/nome dos PDFs. |
| `_ler_data(texto)` | Converte a data gravada para o fuso configurado. Datas antigas sem fuso são lidas como UTC (PostgreSQL) ou horário do computador (SQLite). |
| `percentual_acerto(acertos, total)` | Percentual inteiro, com 0,5 arredondando para cima; `None` se não houver respostas. **É a única fórmula de porcentagem do projeto** — tela, gráficos, resultado e PDF usam ela, por isso os números sempre batem. |

*Perguntas*

| Função | O que faz |
|---|---|
| `_montar_pergunta(linha)` | Transforma a linha do banco em dicionário (decodifica o JSON das alternativas). |
| `listar_perguntas()` | Todas as perguntas, na ordem de cadastro (é a ordem do jogo). |
| `obter_pergunta(id)` | Uma pergunta, ou `None`. |
| `contar_perguntas()` | Quantidade de perguntas (mostrada no menu). |
| `salvar_pergunta(...)` | Cria (sem `pergunta_id`) ou atualiza (com `pergunta_id`). |
| `excluir_pergunta(id)` | Apaga a pergunta; respostas antigas dela continuam nas estatísticas, marcadas como "(excluída)". |
| `restaurar_perguntas_iniciais()` | Apaga todas e grava as 5 de exemplo. |

*Jornadas e estatísticas*

| Função | O que faz |
|---|---|
| `registrar_partida(respostas, participante)` | Grava a jornada e cada resposta; devolve o id da jornada. |
| `_montar_resposta(linha)` / `_montar_partida(linha, respostas)` | Montam os dicionários usados pelas telas (`acertou`, `erros`, `taxa`, data no fuso…). |
| `obter_partida(id)` | Uma jornada com suas respostas (tela de resultado). |
| `listar_partidas()` | Todas as jornadas, mais recentes primeiro, cada uma com `numero` (#1 = a mais antiga). Faz só 2 consultas no total. |
| `medias_por_participante(partidas)` | Agrupa as jornadas por nome (sem diferenciar maiúsculas) e calcula a média de aproveitamento, acertos por jornada e número de jornadas. Jornadas sem nome viram o grupo "Sem identificação", sempre por último. |
| `resumo_partidas()` | Totais gerais: jornadas, respostas, acertos, erros e taxa. |
| `estatisticas_por_pergunta()` | Acertos/erros/taxa de cada pergunta, somados em SQL a partir de `respostas`. Inclui perguntas sem respostas e perguntas já excluídas que têm histórico. |
| `limpar_partidas()` | Apaga todas as jornadas (e, em cascata, as respostas). |

### [Model/perguntas_iniciais.py](Model/perguntas_iniciais.py)

Lista `PERGUNTAS_INICIAIS` com as 5 perguntas de exemplo. Cada item tem `enunciado`, `alternativas` (5 textos),
`correta` (índice 0–4) e `comentario`. É usada na criação do banco e no botão "Restaurar provações padrão".

---

## 8. Funções do Controller (rotas, gráficos e PDF)

### [Controller/menu.py](Controller/menu.py)

| Função | O que faz |
|---|---|
| `inicio()` | Renderiza o menu com o total de perguntas e o limite de caracteres do nome. |

### [Controller/jogo.py](Controller/jogo.py)

A sessão guarda `session['jogo'] = {'perguntas': [ids], 'indice': posição, 'respostas': [...], 'participante': nome}`,
além de `session['participante']` (último nome, para "Nova Jornada") e `session['ultima_partida']` (id para o resultado).

| Função | O que faz |
|---|---|
| `_nome_participante(texto)` | Limpa espaços extras e corta no `TAMANHO_MAXIMO_NOME`. |
| `_pergunta_atual(jogo)` | Pergunta da posição atual; pula as que o admin excluiu durante a partida. |
| `_finalizar(jogo)` | Tira o jogo da sessão, grava a jornada no banco e manda para o resultado. |
| `iniciar()` | Lê o nome (do formulário ou o último usado), monta a lista de perguntas e começa. Sem nome, volta ao menu. |
| `pergunta()` | Mostra a pergunta atual e, se já respondida, o feedback e o botão de avançar. |
| `responder()` | Valida e guarda a alternativa escolhida (impede responder duas vezes). |
| `proxima()` | Avança para a próxima pergunta ou finaliza. |
| `resultado()` | Calcula o percentual e escolhe a **mensagem** final ("Perfeito!", "Muito bem!"…). |

### [Controller/admin.py](Controller/admin.py)

| Função | O que faz |
|---|---|
| `add_app_template_global(...)` (linhas 16–17) | Deixa `fatias_pizza` e `percentual_acerto` disponíveis dentro dos templates e macros. |
| `exigir_acesso()` | Bloqueia a área admin para quem não fez login. |
| `login()` / `sair()` / `inicio()` | Entrada (compara o PIN de forma segura), saída e redirecionamento inicial. |
| `_estatisticas_selecionadas()` | Lê as perguntas marcadas (`?p=`) e devolve todas, as marcadas e as que entram nos gráficos/PDF (sem marcação = todas). |
| `estatisticas()` / `estatisticas_pdf()` | Tela e PDF de acerto por pergunta. |
| `jornadas()` / `jornadas_pdf()` | Tela e PDF do registro de jornadas (média geral, melhor resultado, médias por participante). |
| `limpar_jornadas()` | Botão "Limpar histórico". |
| `_baixar_pdf(conteudo, nome)` | Envia o PDF como download chamado `guardiao-<nome>-<data>.pdf`. |
| `perguntas()` | Lista do grimório. |
| `_ler_formulario()` | Lê e valida o formulário de pergunta; devolve os dados e a lista de erros. |
| `_formulario(...)` | Renderiza o formulário (vazio, preenchido ou com erros). |
| `nova_pergunta()` / `editar_pergunta(id)` / `excluir_pergunta(id)` / `restaurar_perguntas()` | Cadastro de perguntas. |

### [Controller/graficos.py](Controller/graficos.py)

| Função | O que faz |
|---|---|
| `fatias_pizza(acertos, erros)` | Calcula o desenho SVG de cada fatia (verde = acertos, vermelho = erros), começando no topo, no sentido horário. Devolve lista vazia quando não há respostas. Usada pela macro `pizza` em `_graficos.html`. |

### [Controller/relatorio_pdf.py](Controller/relatorio_pdf.py)

Constantes no topo: `NOME_APP` (título dos PDFs), `LARGURA_UTIL` (largura útil da página A4), as **cores**
(`AZUL`, `VERDE`, `VERMELHO`, `OURO`…, iguais às do CSS) e os **estilos de texto** (`ESTILO_TITULO`,
`ESTILO_SECAO`…: fonte, tamanho, cor, espaçamento).

| Função | O que faz |
|---|---|
| `relatorio_estatisticas(resumo, estatisticas, filtrado)` | **PDF de estatísticas**: visão geral (pizza total), tabela de acerto por pergunta e uma pizza por pergunta. |
| `relatorio_jornadas(resumo, partidas, participantes)` | **PDF de jornadas**: visão geral, gráfico de barras e tabela por participante, tabela de todas as jornadas. |
| `_gerar(titulo, elementos)` | Monta o documento A4 com cabeçalho (nome do app, título, data de geração) e rodapé. |
| `_rodape(canvas, documento)` | Escreve o rodapé "O Guardião dos Dados · título" e o número da página. |
| `_resumo_geral(resumo, linhas_extras)` | Bloco "Visão geral" (pizza + números). |
| `_pizza(acertos, erros, diametro)` | Desenha uma pizza (ou um círculo cinza "Sem respostas"). |
| `_legenda(acertos, erros)` | Tabelinha colorida Acertos/Erros/Total. |
| `_bloco_grafico(...)` | Coloca a pizza à esquerda e um conteúdo à direita. |
| `_barras_participantes(participantes, media_geral)` | Gráfico de barras horizontais por participante com a linha tracejada da média geral (divide em blocos de 18 por página). |
| `_tabela_dados(cabecalho, linhas, larguras, colunas_numericas)` | Tabela padrão dos relatórios (cabeçalho bege, números alinhados à direita). |
| `_rotulo_participante(p)` | Nome do participante ou "Sem identificação". |
| `_percentual(taxa)` | `"80%"` ou `"–"`. |
| `_seguro` / `_texto` / `_encurtar` | Ajustam textos para a fonte do PDF (troca caracteres não suportados, como emojis), escapam símbolos e cortam com "…" o que não cabe. |

---

## 9. Templates (View/Página)

### Layout base — [base.html](View/Página/base.html)

Todas as páginas "herdam" deste arquivo com `{% extends 'base.html' %}` e preenchem os **blocos**:

| Bloco | Para que serve |
|---|---|
| `titulo` | Texto da aba do navegador. |
| `classe_body` | Classe do `<body>` (`tela-interna` por padrão; o menu usa `tela-menu`). |
| `corpo` | Página inteira — o menu substitui tudo; as outras páginas mantêm o topo padrão. |
| `topo_titulo` / `topo_direita` | Texto no centro e à direita da barra superior. |
| `abaixo_topo` | Logo abaixo do topo (a barra de progresso do jogo). |
| `conteudo` | O conteúdo principal da página. |
| `scripts` | JavaScript da página, no fim do `<body>`. |

Também carrega as fontes do Google e o CSS (`style.css?v=8` — veja [Cuidados](#12-cuidados-e-armadilhas)).

### Páginas do jogo

| Template | Elementos principais |
|---|---|
| [menuprincipal.html](View/Página/menuprincipal.html) | Botão de engrenagem (admin) no canto, cenário gigante do Guardião, insígnia "Ordem da Cibersegurança & LGPD", título medieval, **fala de boas-vindas**, campo "Quem enfrenta as provações?" e botão "Iniciar Provação". |
| [jogo.html](View/Página/jogo.html) | Barra de progresso, Guardião com expressão conforme a resposta (`indagando` / `orgulhoso` / `alerta`), balão com o enunciado, botões das alternativas, feedback ("Escudo Intacto!" / "Cuidado, viajante!"), comentário "Sabedoria do Guardião" e botão de avançar. Script de atalhos A–E / 1–5. |
| [resultado.html](View/Página/resultado.html) | **Título conquistado** (patente) conforme o percentual, placar, mensagem, lista de acertos/erros e botões "Voltar à Cidadela" / "Nova Jornada". |
| [sem_perguntas.html](View/Página/sem_perguntas.html) | Aviso "Grimório Vazio" quando não há perguntas cadastradas. |

### Páginas da administração

| Template | Elementos principais |
|---|---|
| [admin_login.html](View/Página/admin_login.html) | Campo de PIN. |
| [admin.html](View/Página/admin.html) | Layout da área admin: botão "Sair" e as três **abas**. A aba ativa é descoberta pelo nome da rota. |
| [admin_estatisticas.html](View/Página/admin_estatisticas.html) | 4 indicadores (respostas, acertos, erros, taxa), tabela com caixa de seleção por pergunta e barra de taxa, botões "Gerar gráficos de pizza" e "Exportar PDF", grade de pizzas. Script "marcar todas". |
| [admin_jornadas.html](View/Página/admin_jornadas.html) | 3 indicadores (jornadas, média, melhor), cartão "Média por Participante" (barras), botões "Exportar PDF" e "Limpar histórico", lista expansível de jornadas (nome, data, acertos/erros, %, respostas dadas). |
| [admin_perguntas.html](View/Página/admin_perguntas.html) | Lista de perguntas com "Editar"/"Excluir", botões "Restaurar provações padrão" e "+ Nova provação". |
| [admin_form_pergunta.html](View/Página/admin_form_pergunta.html) | Formulário: enunciado, 5 alternativas com marcação da correta, comentário. |

### Macros (componentes reutilizáveis)

| Arquivo | Macro | O que desenha |
|---|---|---|
| [_guardiao.html](View/Página/_guardiao.html) | `guardiao_svg(humor, classe)` | O medalhão do Guardião. `humor` muda olhos, boca e aura: `indagando`, `orgulhoso`, `alerta` (qualquer outro valor, como `saudacao`, usa a expressão neutra). |
| | `guardiao_fundo_menu()` | O Guardião gigante, torres e halo atrás do menu. |
| | `titulo_medieval()` | O brasão com "O GUARDIÃO / DOS DADOS". |
| [_graficos.html](View/Página/_graficos.html) | `percentual(taxa)` | Escreve `80%` ou `–`. |
| | `pizza(acertos, erros, titulo, subtitulo)` | Um gráfico de pizza com legenda. |
| | `barras_participantes(participantes, media_geral)` | O gráfico de barras da média por participante com a linha tracejada da média geral. |

---

## 10. Estilo visual (View/Estilo/style.css)

**Cores e fontes** ficam em variáveis no início do arquivo (bloco `:root`). Trocar um valor ali muda o site
inteiro:

| Variável | Cor atual | Onde aparece |
|---|---|---|
| `--primaria` / `--primaria-escura` | azul aço / azul noite | Botões principais, títulos, barras de participantes. |
| `--ouro`, `--ouro-claro`, `--ouro-brilho` | dourados | Bordas, destaques, linha da média geral. |
| `--fundo-card-interno`, `--superficie` | tons de pergaminho | Fundo dos cartões e trilhos das barras. |
| `--texto`, `--texto-suave` | grafite / cinza | Textos. |
| `--borda`, `--borda-ouro` | bege / dourado claro | Linhas e contornos. |
| `--sucesso` / `--sucesso-claro` | verde | Acertos. |
| `--erro` / `--erro-claro` | vermelho | Erros. |
| `--raio`, `--sombra` | — | Arredondamento e sombra dos cartões. |
| `--fonte-epica` | Cinzel | Fonte dos títulos. |

O fundo azul da página está no seletor `body` (gradiente logo abaixo de `:root`).

**Seções do arquivo** (procure pelos comentários `/* ---------- ... ---------- */`):

| Seção | O que estiliza |
|---|---|
| Emblema de Título Medieval | O brasão do menu. |
| Insígnias e Personagem | Tamanhos e animações do Guardião (`.guardiao-destaque`, `.guardiao-dialogo`…). |
| Botões | `.botao-primario`, `.botao-secundario`, `.botao-perigo`, `.botao-grande`, `.botao-pequeno`. |
| Cartões | `.cartao` (o "pergaminho" branco). |
| Menu principal | Cenário, cartão do menu, botão da engrenagem. |
| Telas internas | Barra superior (`.topo`) e barra de progresso. |
| Jogo & Diálogo | Balão de fala, alternativas (`.correta`, `.incorreta`, `.esmaecida`), feedback. |
| Resultado | Placar e resumo. |
| Administração | Abas, indicadores, tabelas, lista de jornadas e perguntas. |
| Formulários | Campos de texto e alternativas. |
| `@media (max-width: 600px)` (1º) | Ajustes de celular das telas do jogo. |
| Estatísticas, gráficos de pizza e registro de jornadas | Pizzas, barras de participantes, campo de nome do menu e, no fim, os ajustes de celular dessas telas (`@media 760px` e `600px`). |

---

## 11. Onde alterar cada coisa

### Acesso e configuração

| Quero mudar… | Onde |
|---|---|
| **PIN do admin** | Vercel (produção): variável `QUIZ_PIN_ADMIN` em *Settings → Environment Variables* + *Redeploy*. Local: o padrão `1234` em [Model/config.py linha 10](Model/config.py#L10) — ou defina `QUIZ_PIN_ADMIN` no terminal antes de `python app.py` (PowerShell: `$env:QUIZ_PIN_ADMIN = '...'`). Não grave o PIN real no código: o repositório é público. |
| Fuso horário | Variável `QUIZ_FUSO` ou [config.py linha 22](Model/config.py#L22) (ex.: `America/Manaus`). |
| Limite de caracteres do nome | [config.py `TAMANHO_MAXIMO_NOME`](Model/config.py#L28) (vale para o campo e para o banco). |
| Porta do servidor local | [app.py, última linha](app.py#L37) (`port=5000`). |
| Banco usado | Sem `DATABASE_URL` → SQLite `quiz.db`; com `DATABASE_URL` → PostgreSQL. |

### Textos e conteúdo

| Quero mudar… | Onde |
|---|---|
| **Perguntas de exemplo** (as que vêm de fábrica) | [Model/perguntas_iniciais.py](Model/perguntas_iniciais.py). Só valem para bancos novos ou ao clicar "Restaurar provações padrão" — para o banco atual, edite pelo Grimório na área admin. |
| Perguntas do jogo atual | Área admin → aba **Grimório de Perguntas** (não é preciso mexer no código). |
| Fala de boas-vindas do menu | [menuprincipal.html linha 20](View/Página/menuprincipal.html#L20). Atenção: ela diz "Cinco provações" fixo — se você mudar a quantidade de perguntas, ajuste o texto. |
| "Quem enfrenta as provações?", "Iniciar Provação" | [menuprincipal.html](View/Página/menuprincipal.html#L23-L29). |
| Insígnia "Ordem da Cibersegurança & LGPD" | [menuprincipal.html linha 17](View/Página/menuprincipal.html#L17). |
| Frases do jogo ("O Guardião indaga", "Escudo Intacto!"…) | [jogo.html](View/Página/jogo.html#L25-L58). |
| **Títulos conquistados** (patentes) e as faixas de % | [resultado.html linhas 9–21](View/Página/resultado.html#L9-L21) (100% = Mestre, ≥70 = Paladino, ≥40 = Escudeiro, resto = Aprendiz). |
| **Mensagem final** ("Muito bem!", "Continue praticando!") | [Controller/jogo.py, função `resultado`](Controller/jogo.py#L109). Use as mesmas faixas das patentes. |
| Texto das abas do admin | [admin.html](View/Página/admin.html#L10-L12). |
| Texto "Sem identificação" (jornadas sem nome) | Tela: [_graficos.html](View/Página/_graficos.html) e [admin_jornadas.html](View/Página/admin_jornadas.html); PDF: [`_rotulo_participante`](Controller/relatorio_pdf.py#L62) e `relatorio_jornadas`. |

### Nome do aplicativo

"O Guardião dos Dados" aparece em vários lugares; para renomear, troque em todos:

- bloco `titulo` de cada template (`base.html`, `admin*.html`, `jogo.html`, `resultado.html`, `sem_perguntas.html`);
- o brasão em [_guardiao.html, macro `titulo_medieval`](View/Página/_guardiao.html#L271) (textos "O GUARDIÃO" e "DOS DADOS" do SVG e o `<h1>` escondido usado por leitores de tela);
- [`NOME_APP` em relatorio_pdf.py](Controller/relatorio_pdf.py#L17) (título e rodapé dos PDFs);
- o prefixo do arquivo baixado `guardiao-` em [`_baixar_pdf`](Controller/admin.py#L110);
- títulos do `README.md` e deste manual.

Dica: no VS Code, **Ctrl+Shift+F** procurando "Guardião dos Dados" lista todos.

### Visual

| Quero mudar… | Onde |
|---|---|
| **Cores do site** | Variáveis no topo do [style.css](View/Estilo/style.css) (`:root`). |
| Cores dos PDFs | Constantes no topo do [relatorio_pdf.py](Controller/relatorio_pdf.py#L21-L30) (mantenha iguais às do CSS). |
| Cor das pizzas na tela | `.fatia-acertos` / `.fatia-erros` no style.css (seção de estatísticas). |
| Cor das barras de participantes / linha da média | `.barra-preenchida`, `.barra-anonima .barra-preenchida`, `.barra-marca-media` no style.css. |
| Fontes dos títulos | Link do Google Fonts em [base.html](View/Página/base.html#L9) + `--fonte-epica` no CSS. |
| Desenho do Guardião | Macros em [_guardiao.html](View/Página/_guardiao.html) (cada parte tem um comentário: pluma, elmo, barba, escudo…). |
| Layout no celular | Blocos `@media (max-width: 600px)` e `760px` do style.css. |

### Regras do jogo

| Quero mudar… | Onde |
|---|---|
| Ordem das perguntas | [`jogo.iniciar`](Controller/jogo.py#L35): hoje segue a ordem de cadastro. Para embaralhar, adicione `random.shuffle(ids)` (com `import random`) depois de montar `ids`. |
| Fórmula da porcentagem | [`percentual_acerto`](Model/repositorio.py#L100) (vale para o site e os PDFs). |
| Média por participante (agrupamento) | [`medias_por_participante`](Model/repositorio.py#L160). |
| Número de alternativas | Exige mexer em vários pontos juntos: `LETRAS` e `QTD_ALTERNATIVAS` em config.py, o atalho de teclado em [jogo.html](View/Página/jogo.html#L83-L84) (`'ABCDE'` e `[1-5]`), as perguntas de `perguntas_iniciais.py` e as perguntas já cadastradas no banco. |

### Banco de dados

| Quero… | Como |
|---|---|
| Adicionar uma coluna | 1) inclua no `ESQUEMA` de [banco.py](Model/banco.py#L24) (para bancos novos); 2) em [`_atualizar_esquema`](Model/banco.py#L134) adicione um `if not _coluna_existe(...)` com o `ALTER TABLE` (para bancos já existentes, como o Neon); 3) ajuste as consultas em `repositorio.py`. |
| Zerar o banco local | Pare o servidor e apague o arquivo `quiz.db` — ele é recriado na próxima execução. |
| Zerar só o histórico | Área admin → Registro de Jornadas → **Limpar histórico**. |

---

## 12. Cuidados e armadilhas

- **CSS não atualiza no navegador?** Depois de editar o `style.css`, aumente o número em
  [base.html](View/Página/base.html#L10) (`v='8'` → `v='9'`). Isso força navegadores e o Vercel a baixarem a
  versão nova.
- **Ponto e vírgula no `ESQUEMA`**: o SQL de criação é dividido em comandos pelo `;`. Não use `;` dentro dos
  comentários `--` do `ESQUEMA`, ou a criação do banco quebra.
- **Consultas SQL**: escreva sempre com `?` (ex.: `WHERE id = ?`) e passe os valores separados — a classe
  `Conexao` converte para o PostgreSQL. Nunca monte SQL juntando texto com valores digitados pelo usuário.
- **`app = criar_app()`** em `app.py` precisa continuar existindo com esse nome, ou o Vercel não encontra o
  aplicativo (`FLASK_ENTRYPOINT_NOT_FOUND`).
- **Dependências novas** precisam entrar no `requirements.txt`, senão funcionam no seu computador mas falham
  no Vercel.
- **Sessão no Vercel**: sem `QUIZ_SECRET_KEY` definida, jogadores podem perder a jornada no meio.
- **SQLite no Vercel** (sem Neon) funciona, mas os dados somem a cada reinício — use sempre o Neon em produção.
- **Modo debug**: `python app.py` roda com `debug=True`, que recarrega o servidor ao salvar arquivos. É só
  para uso local; o Vercel não usa esse trecho.
- **Faixas de resultado em dois lugares**: as patentes (resultado.html) e as mensagens (jogo.py) usam as mesmas
  faixas de percentual (100 / 70 / 40). Se mudar uma, mude a outra.
