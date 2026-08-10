---
id: adr-002
type: Decision
title: Engine interno — fork do OpenCode (tcecode-agent)
status: superseded
date: 2026-08-10
superseded_by: adr-009-fork-opencode.md
---

# ADR-002 — Engine interno: OpenCode (histórico)

> **Supersedido por ADR-009.** Fork do OpenCode implementado em 2026-08-10.
> Este ADR documenta a decisão original de não fazer fork (Fases 1–2 iniciais).

## Decisão original

OpenCode usado diretamente, sem fork. Aceitávamos limitações de branding (logo "opencode" na TUI, texto "opencode -s" no epilogue, auto-update do upstream aparecendo).

## Por que foi supersedida

O fork foi implementado na mesma fase após validação técnica mostrar que o custo é baixo (mudanças mínimas em 3 arquivos, build em ~1 min com Bun) e o benefício imediato é real: identidade institucional completa desde a Fase 2.

Ver [adr-009-fork-opencode](/decisions/adr-009-fork-opencode.md) para a decisão atual.

## Relacionamentos

- [adr-001-stack](/decisions/adr-001-stack.md)
- [adr-009-fork-opencode](/decisions/adr-009-fork-opencode.md)
- [overview](/architecture/overview.md)
