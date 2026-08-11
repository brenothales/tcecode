---
id: tce-ai-platform
type: index
title: Institutional AI Engineering Platform — TCE
status: active
---

# Institutional AI Engineering Platform

Plataforma institucional de engenharia de software assistida por IA para as squads do TCE. O desenvolvedor instala e executa `tcecode` — o produto institucional — sem expor credenciais de provedores de IA.

> O código pertence à squad. Os padrões pertencem à instituição. O contexto pertence ao projeto. Os modelos pertencem à plataforma.

## Architecture

- [overview](/architecture/overview.md) — Visão geral, componentes, Golden Path, fluxo do agente
- [ai-gateway](/architecture/ai-gateway.md) — LiteLLM: roteamento, modelos lógicos, fallback, observabilidade
- [security-model](/architecture/security-model.md) — Threat model, RBAC, gestão de credenciais
- [logical-models](/architecture/logical-models.md) — Modelos lógicos institucionais (institutional-coding, etc.)
- [rbac-roles](/architecture/rbac-roles.md) — Papéis: AI_PLATFORM_ADMIN, AI_DEVELOPER, AI_AUDITOR, etc.
- [multi-agent](/architecture/multi-agent.md) — A2A: agentes especializados (Fase 5)

## Decisions

- [adr-001-stack](/decisions/adr-001-stack.md) — tcecode como produto, OpenCode como engine interno (sem fork)
- [adr-002-coding-agent](/decisions/adr-002-coding-agent.md) — OpenCode sem fork — engine gerenciado pelo tcecode
- [adr-003-ai-gateway](/decisions/adr-003-ai-gateway.md) — LiteLLM Proxy
- [adr-004-identity](/decisions/adr-004-identity.md) — Keycloak + OIDC (Fase 2)
- [adr-005-repositories](/decisions/adr-005-repositories.md) — Multi-repo strategy
- [adr-006-branding](/decisions/adr-006-branding.md) — Branding do tcecode: limitações sem fork
- [adr-007-traefik](/decisions/adr-007-traefik.md) — Traefik como reverse proxy, atualmente v3.6 (substituindo Nginx)
- [adr-008-phase2-identity](/decisions/adr-008-phase2-identity.md) — Fase 2: Keycloak + ROPC Grant + JWT institucional
- [adr-009-fork-opencode](/decisions/adr-009-fork-opencode.md) — Fork thin do OpenCode: tcecode-agent com branding TCE CODE
- [adr-010-install-distribution](/decisions/adr-010-install-distribution.md) — Instalador one-liner (curl/irm) — clona e builda o fork localmente, sem CI de binários

## Domains

_(a preencher conforme domínios do TCE forem mapeados)_

## Agents

- [tce-agent](/agents/tce-agent.md) — Agente principal (OpenCode + AGENTS.md institucional)

## Patterns

- [agent-loop](/patterns/agent-loop.md) — Ciclo plan→act→observe

## Development

- [phases-roadmap](/development/phases-roadmap.md) — 6 fases: Foundation → Governance
- [quality-gate](/development/quality-gate.md) — Checklist do agente antes de concluir tarefa
- [okf-mermaid-setup](/development/okf-mermaid-setup.md) — Habilitar diagramas Mermaid no viewer OKF

## Status da Fase 1 — Foundation ✅

Concluída e validada em 2026-08-10.
Fluxo end-to-end: `tcecode` → OpenCode → **Traefik** → LiteLLM → AI Providers ✅
Nginx substituído por Traefik (ADR-007, atualizado para v3.6 em 2026-08-10 por incompatibilidade de API Docker com Engine 29.x). Stack 100% production-like.

## Status da Fase 2 — Identity ✅

Concluída e validada em 2026-08-10.
`tcecode login` → Keycloak ROPC → JWT (squad + roles) → Bearer token no LiteLLM ✅
8 serviços rodando: traefik, litellm, postgres, postgres-keycloak, redis, keycloak, prometheus, grafana.
**Limitação documentada**: LiteLLM `enable_jwt_auth` é enterprise-only — JWT é identidade no tcecode, virtual key é acesso ao LiteLLM. Ver ADR-008 §lição 4.

## Status do Fork (ADR-009) ✅

Fork `tcecode-agent` buildado a partir de `brenothales/opencode` (branch `dev`) e validado end-to-end em 2026-08-10. Dois bugs de auth encontrados e corrigidos no `tcecode` CLI (não no fork): `npm` do provider ausente e `gateway_url` em `http://` em vez de `https://` — ambos causavam `No api key passed in` mesmo com virtual key válida. Ver `log.md` para detalhes completos.

## Status dos Providers (validado em 2026-08-10)

- `institutional-reasoning` (OpenAI `o3`) ✅ funcionando ponta a ponta
- `institutional-coding` (Anthropic Claude) ❌ sem crédito na conta
- `institutional-fast` (Gemini `gemini-2.0-flash`) ❌ quota 0 no tier gratuito do projeto Google Cloud/AI Studio (persiste mesmo após trocar a API key — é o projeto, não a chave)
