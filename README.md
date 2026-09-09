# Hotel Booking API 

Sistema de reserva de quartos de hotel — projeto da disciplina de Integração DevOps 

## Funcionalidades

- Cadastro e listagem de quartos
- Criação de reservas com validação de datas e checagem de conflito de disponibilidade
- Cancelamento de reservas
- Verificação de disponibilidade de um quarto em um período

## Como rodar localmente

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

Acesse:
- Front-end: http://localhost:8000
- Documentação interativa da API (Swagger): http://localhost:8000/docs


## Infraestrutura e CI/CD

Este projeto conta com:
- Pipeline de Integração Contínua (GitHub Actions) que roda os testes automatizados e builda a imagem Docker a cada push/PR.
- Conteinerização via `Dockerfile` e `docker-compose.yml`.
- Estratégia de branching Trunk-Based com proteção da branch `main` (ver `CONTRIBUTING.md`).

### Como rodar via Docker

\`\`\`bash
docker compose up --build
\`\`\`

