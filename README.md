# O Guardião dos Dados

Quiz de perguntas e respostas em Python (Flask + SQLite), organizado em Model / View / Controller.

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
| `QUIZ_PIN_ADMIN`  | `1234`              | PIN da área administrativa                  |
| `QUIZ_SECRET_KEY` | aleatória por início | Chave das sessões (defina para mantê-las ao reiniciar) |
| `QUIZ_BANCO`      | `quiz.db`           | Caminho do arquivo SQLite                   |

## Estrutura

- `app.py` — ponto de entrada
- `Model/` — configuração, banco SQLite, perguntas iniciais e repositório de dados
- `Controller/` — rotas: menu, jogo e área administrativa
- `View/Página/` — templates HTML (Jinja) · `View/Estilo/` — CSS
