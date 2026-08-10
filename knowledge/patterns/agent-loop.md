---
type: Architecture Pattern
title: Agent Loop (Plan → Act → Observe)
description: Ciclo de execução do agente — o LLM planeja, escolhe uma ferramenta, executa, observa o resultado e itera até concluir.
tags: [agent, loop, llm, tools]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
status: draft
---

# Agent Loop

Padrão central de execução do TCE Agent. O agente opera em ciclos até decidir que a tarefa está concluída ou atingir o limite de iterações.

## Pseudocódigo

```python
while not done and iterations < MAX_ITER:
    response = llm.complete(messages + tool_results)
    if response.has_tool_call:
        result = tools.execute(response.tool_call)
        messages.append(tool_result(result))
    else:
        done = True
        output(response.text)
```

## Considerações

- Limite de iterações evita loops infinitos em caso de falha de ferramenta.
- Cada tool_result é adicionado ao contexto acumulado — custo de tokens cresce por ciclo.
- Ferramentas destrutivas (write_file, run_command) devem ter confirmação explícita do usuário.

## Relacionamentos

- [tce-agent](/agents/tce-agent.md)
- [overview](/architecture/overview.md)
