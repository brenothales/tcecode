# Log

## 2026-08-10 (atualização — migração para Traefik)

**Nginx substituído por Traefik v3.2** (ADR-007). Stack 100% production-like revalidado.

- `traefik/traefik.yaml` e `traefik/dynamic.yaml` criados (roteamento, middlewares, TLS)
- Lições registradas: label conflict multi-service, replacePath middleware, SSL em urllib
- `tcecode status` corrigido para ignorar cert autoassinado (ssl.CERT_NONE)
- Fluxo validado: `tcecode status` → Gateway: online; `/v1/models` retorna 3 modelos institucionais ✅

---

## 2026-08-10

**Fase 1 — Foundation concluída e validada.**

**Implementação:**
- Stack Docker production-like subido: LiteLLM + Nginx (TLS) + Redis + Postgres + Prometheus + Grafana
- `tcecode` CLI criado como produto institucional (Python/Typer) — OpenCode gerenciado internamente como engine, invisível ao desenvolvedor
- `tcecode update` detecta e vincula instalação existente do OpenCode no sistema
- Virtual key criada para `squad-test` via `make create-squad-key`
- Fluxo end-to-end validado: `tcecode → OpenCode → Nginx → LiteLLM → OpenAI ✅`

**Decisões registradas:**
- ADR-001 atualizado: `tcecode` é o produto, não um wrapper — OpenCode é detalhe de implementação
- ADR-002 atualizado: sem fork do OpenCode nas Fases 1–4
- ADR-006 criado: limitações de branding da TUI sem fork — aceitas para Fase 1

**Problemas encontrados e resolvidos:**
- `internal: true` no Docker bloqueava egress do LiteLLM para providers externos → litellm adicionado à rede `public`
- Health check usava `curl` (ausente na imagem LiteLLM) → corrigido para `python3 urllib`
- Health endpoint `/health` exige auth no LiteLLM → nginx proxy para `/health/liveliness`
- Download do OpenCode falhou (repo transferido + urllib sem redirect handling) → `agent.py` detecta instalação existente no sistema

**Status dos providers:**
- `institutional-reasoning` → OpenAI ✅
- `institutional-coding` → Anthropic ❌ sem crédito
- `institutional-fast` → Gemini ❌ free tier esgotado

**Próxima fase:** Fase 2 — Identity (Keycloak + OIDC + JWT + RBAC)

---

## 2026-08-09

Bundle criado. Sessão de arquitetura completa. Definição e documentação de toda a plataforma institucional.

**Decisões tomadas:**
- ADR-001: Stack — Python/Typer + LiteLLM
- ADR-002: OpenCode como engine
- ADR-003: LiteLLM Proxy como AI Gateway
- ADR-004: Keycloak + OIDC para identidade (Fase 2)
- ADR-005: Multi-repo strategy
