## Orquestração local (Docker Compose)

A aplicação sobe integrada ao PostgreSQL com um único comando.

### Arquitetura

| Serviço | Imagem        | Função                              | Porta |
|---------|---------------|-------------------------------------|-------|
| `app`   | build local   | API FastAPI + front-end estático    | 8000  |
| `db`    | postgres:16   | Banco de dados (volume `pgdata`)    | interna |

- `app` lê `DATABASE_URL` (já suportado em `app/database.py`) e conecta em `db` pela rede `backend`.
- `depends_on` com `condition: service_healthy`: a API só inicia depois que o Postgres responde ao `pg_isready`.
- Healthcheck da API em `/health`.
- Dados persistidos no volume nomeado `pgdata`.
- Credenciais vêm do arquivo `.env` (não versionado), nada fica hardcoded.

### Como executar

```bash
cp .env.example .env        # ajuste a senha
docker compose up --build -d
docker compose ps           # app e db devem estar "healthy"
```

- Front-end: http://localhost:8000
- Swagger: http://localhost:8000/docs

### Comandos úteis

```bash
docker compose logs -f app      # logs da API
docker compose exec db psql -U hotel -d hotel -c "\dt"   # ver tabelas
docker compose down             # para (mantém dados)
docker compose down -v          # para e apaga o banco
```

### Evidências para a entrega

1. Print de `docker compose ps` com os dois serviços `healthy`.
2. Print do front-end/Swagger funcionando.
3. Cadastrar um quarto, rodar `docker compose down` e `up` de novo: o quarto continua lá (prova da persistência).
