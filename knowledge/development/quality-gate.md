---
id: quality-gate
type: Runbook
title: Quality Gate do Agente
status: active
---

# Quality Gate do Agente

Antes de considerar uma implementação concluída, o agente verifica:

## Código

- [ ] Compila sem erros
- [ ] Nenhum warning não justificado
- [ ] Arquitetura adequada (Hexagonal/Clean quando aplicável, sem lógica em controller)
- [ ] SOLID respeitado
- [ ] Sem dependências circulares

## Testes

- [ ] Testes unitários para comportamento relevante
- [ ] Testes de integração para adapters/infra
- [ ] Todos os testes passam
- [ ] Cobertura razoável (sem obsessão por percentual — cobertura de comportamento, não de linhas)

## Segurança

- [ ] Nenhum secret hardcoded (API key, password, connection string)
- [ ] Validação de entrada nos boundaries do sistema
- [ ] Sem SQL injection, command injection, XSS
- [ ] Princípio do menor privilégio respeitado
- [ ] Logs não contêm dados sensíveis

## Observabilidade

- [ ] Logs estruturados (JSON) com nível adequado
- [ ] Métricas relevantes instrumentadas (se aplicável)
- [ ] Trace propagado (se aplicável)
- [ ] Health endpoint presente (se serviço)

## Dependências

- [ ] Nenhuma dependência nova sem justificativa
- [ ] Dependências verificadas quanto a vulnerabilidades conhecidas

## Documentação

- [ ] README atualizado se comportamento externo mudou
- [ ] OpenAPI atualizado se endpoint mudou
- [ ] ADR criado se decisão arquitetural relevante foi tomada

## OKF

- [ ] `.okf/` atualizado se houver novo conhecimento permanente relevante
- [ ] Nenhum secret no OKF

## Git

- [ ] Git diff revisado antes de commit
- [ ] Commit message descritiva
- [ ] Nenhum arquivo desnecessário incluído (.env, *.secret, etc.)

---

O agente não marca a tarefa como concluída sem passar por este checklist.
Para tarefas simples (refatorações cosméticas, renomeações), verificações de arquitetura e OKF podem ser puladas.

## Relacionamentos

- [overview](/architecture/overview.md)
- [security-model](/architecture/security-model.md)
