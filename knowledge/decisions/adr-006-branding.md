---
id: adr-006
type: Decision
title: Branding do tcecode — resolvido via fork (ADR-009)
status: superseded
date: 2026-08-10
superseded_by: adr-009-fork-opencode.md
---

# ADR-006 — Branding do tcecode (histórico)

## Contexto

Ao executar `tcecode`, o OpenCode abre sua TUI exibindo "opencode" na splash screen e o nome real do modelo do provider (ex: "GPT-5.3 Chat · OpenAI") em vez dos nomes lógicos institucionais (ex: "institutional-reasoning"). Isso foi observado em validação da Fase 1.

## Decisão

**Aceitar as limitações de branding nas Fases 1–4.** Não fazer fork do OpenCode agora.

O `tcecode` é o produto institucional no ponto de vista do desenvolvedor: é o que ele instala, configura e invoca. O que aparece dentro da TUI é detalhe de implementação do engine — aceitável enquanto o fork não tiver justificativa técnica além de cosmética.

## Limitações conhecidas (sem fork)

| O que aparece | O que deveria aparecer | Solução sem fork |
|---|---|---|
| "opencode" na splash | "tcecode" | Não possível sem fork |
| "GPT-5.3 Chat · OpenAI" | "institutional-reasoning" | Não possível sem fork |
| Dicas do OpenCode ("Set rm -rf...") | Dicas institucionais | Parcialmente via AGENTS.md |

## Quando reavaliar

Fork entra em pauta se qualquer condição abaixo for verdadeira:

- Branding institucional for requisito regulatório ou de auditoria
- A TUI precisar de customizações funcionais (não apenas cosméticas)
- O OpenCode upstream introduzir breaking changes incompatíveis
- Surgir engine alternativo com melhor suporte a customização

## Consequências

- Documentação para desenvolvedores deve esclarecer que a TUI interna é o engine do tcecode
- Onboarding deve focar no comando `tcecode`, não na UI interna
- Fase 5 (Agent Ecosystem) reavaliará fork ou engine próprio

## Relacionamentos

- [adr-001-stack](/decisions/adr-001-stack.md)
- [adr-002-coding-agent](/decisions/adr-002-coding-agent.md)
