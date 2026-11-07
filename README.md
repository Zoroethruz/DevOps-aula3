# Hotel Booking API 🏨

Sistema de reserva de quartos de hotel — projeto da disciplina de Integração DevOps (UniCEUB, 2026_2, prof. Danilo Silva).

## Stack

- **Backend:** Python + FastAPI
- **Banco de dados:** PostgreSQL 16 (via Docker Compose) — SQLite como fallback para rodar sem Docker (`app/database.py` lê `DATABASE_URL`)
- **Front-end:** HTML + JavaScript puro, servido pelo próprio FastAPI
- **Testes:** pytest + FastAPI TestClient (suíte em `tests/`, roda contra SQLite em memória)
- **Containerização:** Dockerfile (usuário não-root) + Docker Compose (app + Postgres)
- **CI/CD:** GitHub Actions — build, testes, build da imagem Docker, push para o GHCR e simulação de rollback

## Funcionalidades

- Cadastro, listagem, busca/filtro, edição e exclusão (soft delete) de quartos
- Criação de reservas com validação de datas e checagem de conflito de disponibilidade
- Cancelamento de reservas
- Verificação de disponibilidade de um quarto em um período

## Como rodar

### Opção 1 — Docker Compose (recomendado)

Sobe a API já integrada ao PostgreSQL, com persistência de dados.

```bash
cp .env.example .env        # Senha: senhadevops123
docker compose up --build -d
docker compose ps           # app e db devem aparecer como "healthy"
```

- Front-end: http:pytest tests/ -v//localhost:8000
- Swagger: http://localhost:8000/docs

Mais detalhes (arquitetura dos serviços, comandos úteis, roteiro de evidências para a entrega) em [`README-orquestracao.md`](./README-orquestracao.md).

### Opção 2 — Local, sem Docker (usa SQLite)

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

## Rodar os testes

```bash
pytest tests/ -v
```

## Estrutura do projeto

```
app/
  main.py        # rotas da API
  models.py      # modelos SQLAlchemy (Room, Reservation)
  schemas.py     # schemas Pydantic (validação de entrada/saída)
  crud.py        # regras de negócio (busca, disponibilidade, soft delete)
  database.py    # conexão com o banco (SQLite local / Postgres via DATABASE_URL)
static/
  index.html     # front-end
tests/
  test_app.py    # suíte de testes automatizados
  conftest.py    # fixtures de teste (banco em memória)
Dockerfile               # imagem da aplicação (usuário não-root)
docker-compose.yml        # orquestração local: app + PostgreSQL
.env.example               # modelo de variáveis de ambiente (copiar para .env)
.github/workflows/
  ci.yml                   # testes automatizados a cada push/PR
  cd.yml                   # build + push da imagem para o GHCR e deploy simulado
  rollback.yml              # simulação automatizada de rollback entre versões
```

## Pipeline CI/CD

- **CI** (`ci.yml`): a cada push/PR em `main` ou `código`, instala dependências e roda a suíte de testes.
- **CD** (`cd.yml`): builda a imagem Docker, publica no GHCR com tag semântica (`vX.Y.Z`) e `latest`, e simula o deploy em ambiente de homologação via `docker compose`.
- **Rollback** (`rollback.yml`): builda a versão atual e a anterior (`HEAD^`), sobe a atual, e simula a troca para a versão anterior sem derrubar o banco — valida que o rollback é possível sem perda de dados.
- Credenciais do ambiente de homologação (ex: `STAGING_DB_PASSWORD`) ficam nos **Secrets do GitHub Actions**, nunca no código.