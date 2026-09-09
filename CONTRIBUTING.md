# Contribuição

## Estratégia de branches

Este projeto utiliza uma estratégia Trunk-Based simplificada:

- `main` é a branch principal e deve permanecer estável.
- Alterações devem ser feitas em branches curtas.
- Exemplos: `feat/nova-funcionalidade`, `fix/corrige-reserva`, `infra/marco1`.
- O merge na `main` deve ser realizado por Pull Request.
- O Pull Request só deve ser aprovado quando o CI estiver verde.

## Padrão de commits

Utilizamos Conventional Commits:

- `feat:` nova funcionalidade
- `fix:` correção
- `test:` testes
- `docs:` documentação
- `refactor:` refatoração
- `chore:` manutenção e infraestrutura

Exemplo:

```bash
git commit -m "chore: adiciona Docker e pipeline de CI"
```
