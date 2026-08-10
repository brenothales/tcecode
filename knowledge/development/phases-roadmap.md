---
id: phases-roadmap
type: Runbook
title: Roadmap de Implementação — Fases
status: active
---

# Roadmap de Implementação

## Fase 1 — Foundation ✅ Concluída (2026-08-10)

```
tcecode CLI (Python/Typer)
+ OpenCode (engine interno, sem fork)
+ LiteLLM Proxy (AI Gateway)
+ Nginx (reverse proxy + TLS)
+ Redis (rate limiting)
+ Postgres (quotas/audit)
+ Prometheus + Grafana
+ Virtual keys por squad
```

**Validado:** fluxo `tcecode → OpenCode → Nginx → LiteLLM → OpenAI` funcionando end-to-end.

**Fork implementado (ADR-009):** branding resolvido — `tcecode-agent` com logo TCE CODE, epilogue correto, auto-update desabilitado. ADR-006 supersedido.

**Providers ativos:**
- `institutional-reasoning` → OpenAI ✅
- `institutional-coding` → Anthropic ❌ (sem crédito)
- `institutional-fast` → Gemini ❌ (free tier esgotado)

---

## Fase 2 — Identity ✅ Concluída (2026-08-10)

```
Keycloak 26.0 + OIDC (ROPC Grant)
+ JWT institucional com squad + roles
+ tcecode login/logout/status
+ Token refresh automático (30s buffer)
+ Keycloak roteado via Traefik file provider
```

**Stack:** postgres-keycloak + keycloak + realm tce-ai + cliente tcecode-cli

**Separação de responsabilidades:**
- JWT = identidade do desenvolvedor no tcecode (quem está usando, rastreabilidade)
- Virtual key = credencial de acesso ao LiteLLM (por squad — mantida da Fase 1)

**Limitação conhecida:** LiteLLM JWT auth (`enable_jwt_auth`) é feature enterprise-only.
**Fork implementado (ADR-009):** `tcecode-agent` com branding TCE CODE. Build: `bun run script/build.ts --single --skip-embed-web-ui`.
Caminho para Fase 3: middleware Traefik (ForwardAuth) valida JWT e injeta virtual key do squad.

**Providers ativos:**
- `institutional-reasoning` → OpenAI ✅
- `institutional-coding` → Anthropic ❌ (sem crédito)
- `institutional-fast` → Gemini ❌ (free tier esgotado)

---

## Fase 3 — Institutional Knowledge

```
Skills institucionais completas (20+ tecnologias)
+ AGENTS.md global e por squad
+ .okf/ integrado ao tcecode (leitura automática de contexto)
+ Template de novo projeto (Spring Boot + observabilidade + security)
+ tcecode new-project <nome>
```

---

## Fase 4 — Institutional Tools (MCP)

```
MCP Server: GitLab
MCP Server: Jira
MCP Server: Kubernetes
MCP Server: OpenSearch
MCP Server: Grafana / Logs
MCP Server: CI/CD
MCP Server: Service Catalog
```

---

## Fase 5 — Agent Ecosystem (A2A)

```
Architecture Agent
Security Agent
DevOps Agent
Database Agent
Testing Agent
Documentation Agent
```

Reavaliação de fork do OpenCode nesta fase se necessário.

---

## Fase 6 — Governance

```
Audit logs completos com OpenTelemetry
+ Cost reports por squad/projeto/mês
+ Quota enforcement com alertas
+ AI Governance policies (LGPD, uso responsável)
+ Compliance reports
+ Vault para rotação automática de secrets
```

## Relacionamentos

- [overview](/architecture/overview.md)
- [adr-001-stack](/decisions/adr-001-stack.md)
- [adr-006-branding](/decisions/adr-006-branding.md)
