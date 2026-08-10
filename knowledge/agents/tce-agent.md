---
type: Service
title: TCE Agent
description: Agente de IA especializado no contexto do Tribunal de Contas — processa prompts, executa ferramentas e entrega resultados via CLI.
tags: [agent, tce, cli, ai]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
status: draft
---

# TCE Agent

Agente de IA que encapsula o loop de raciocínio e execução de ferramentas. Recebe um prompt do usuário, decide quais ferramentas usar e itera até completar a tarefa.

## Casos de uso planejados

- Análise de contratos e licitações
- Geração de relatórios de auditoria
- Busca e RAG sobre legislação e acórdãos
- Assistência a código interno do TCE

## Ferramentas previstas

| Ferramenta | Descrição |
|---|---|
| `read_file` | Lê arquivo local |
| `write_file` | Escreve/edita arquivo |
| `search` | Busca semântica em documentos TCE |
| `run_command` | Executa comando shell (modo controlado) |
| `api_tce` | Chama APIs internas do TCE |

## Relacionamentos

- [overview](/architecture/overview.md)
- [agent-loop](/patterns/agent-loop.md)
- [adr-001-stack](/decisions/adr-001-stack.md)
