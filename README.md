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

