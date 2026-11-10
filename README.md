# O Guardião dos Dados

**Autor:** Bruno Fioravanti

Quiz de cibersegurança e LGPD em Python (Flask), com SQLite local ou PostgreSQL (Neon) no Vercel,
organizado em Model / View / Controller.

📘 **[MANUAL.md](MANUAL.md)** explica cada arquivo, função, página e variável, e onde alterar cada coisa.

## Executar

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Acesse http://127.0.0.1:5000. O banco `quiz.db` é criado na primeira execução com 5 perguntas de exemplo.

## Configuração (variáveis de ambiente, opcionais)

| Variável          | Padrão              | Descrição                                   |
|-------------------|---------------------|---------------------------------------------|
| `QUIZ_PIN_ADMIN`  | `1234` (só local)   | PIN da área administrativa — em produção defina sempre esta variável |
| `QUIZ_SECRET_KEY` | aleatória por início | Chave das sessões (defina para mantê-las ao reiniciar) |
| `QUIZ_BANCO`      | `quiz.db`           | Caminho do arquivo SQLite                   |
| `DATABASE_URL`    | —                   | URL do PostgreSQL; quando definida, substitui o SQLite |
| `QUIZ_FUSO`       | `America/Sao_Paulo` | Fuso horário das datas exibidas e gravadas  |

## Área administrativa (`/admin`, protegida por PIN)

- **Estatísticas** — acertos, erros e taxa de acerto de cada pergunta. Marque perguntas para gerar
  gráficos de pizza (acertos x erros) na tela ou exportar o relatório em PDF com os gráficos.
- **Registro de Jornadas** — cada conclusão do questionário, com participante, data, acertos, erros,
  aproveitamento e as respostas dadas, além do gráfico de média por participante; também exporta PDF.
- **Grimório de Perguntas** — cadastro, edição e exclusão de perguntas.

Cada resposta é gravada na tabela `respostas` (pergunta, alternativa escolhida e correta) quando a jornada
termina; as estatísticas são calculadas a partir dela. "Limpar histórico" apaga as jornadas e, com elas,
as estatísticas.

## Deploy no Vercel

O Vercel usa a instância `app` definida em `app.py`. Em produção os dados ficam num PostgreSQL
(Neon); localmente, sem `DATABASE_URL`, o app continua usando o SQLite (`quiz.db`).

1. No projeto do Vercel: **Storage → Create Database → Neon** e conecte ao projeto. A integração cria a
   variável `DATABASE_URL` automaticamente.
2. Em **Settings → Environment Variables**, defina `QUIZ_SECRET_KEY` (gere com
   `python -c "import secrets; print(secrets.token_hex(32))"`) e `QUIZ_PIN_ADMIN`.
3. Faça um novo deploy. Na primeira requisição as tabelas são criadas e as perguntas de exemplo cadastradas.

Sem `DATABASE_URL` o app ainda funciona no Vercel, mas com SQLite em `/tmp`, que é temporário:
perguntas cadastradas e histórico de partidas se perdem.

## Estrutura

- `app.py` — ponto de entrada
- `Model/` — configuração, banco (SQLite/PostgreSQL), perguntas iniciais e repositório de dados
- `Controller/` — rotas (menu, jogo e área administrativa), gráficos de pizza e relatórios em PDF
- `View/Página/` — templates HTML (Jinja) · `View/Estilo/` — CSS

## Autoria

Desenvolvido por **Bruno Fioravanti**.
