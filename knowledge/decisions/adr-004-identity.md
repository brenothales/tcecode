---
id: adr-004
type: Decision
title: Identidade e Autenticação — Keycloak + OIDC
status: accepted
date: 2026-08-09
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
---

# ADR-004 — Identidade: Keycloak + OIDC

## Contexto

A plataforma precisa identificar cada desenvolvedor nas requisições ao AI Gateway para aplicar RBAC, quotas, auditoria e rastreamento de custos por squad/projeto. A instituição já utiliza Keycloak em outros sistemas — reaproveitar é o caminho natural.

## Decisão

**Keycloak** é o Identity Provider da plataforma, integrado via **OIDC / OAuth2**.

Cada requisição ao AI Gateway carrega um JWT emitido pelo Keycloak contendo identidade do usuário, squad, projeto e permissões.

## Fluxo de autenticação

```
tce-ai (CLI)
    │
    │  1. Device Authorization Flow (PKCE)
    ▼
Keycloak
    │  2. JWT emitido
    ▼
tce-ai armazena token (~/.tce-ai/token.json)
    │
    │  3. Authorization: Bearer <jwt>
    ▼
LiteLLM Proxy
    │  4. Valida JWT (JWKS endpoint do Keycloak)
    │  5. Extrai claims: user, squad, project, roles
    ▼
Model Router + RBAC + Quota
```

## Claims JWT relevantes

```json
{
  "sub": "breno.thales@tce.gov.br",
  "squad": "squad-dados",
  "project": "sistema-ged",
  "roles": ["AI_DEVELOPER"],
  "preferred_username": "breno.thales"
}
```

## Fase de implementação

- **Fase 1 (Foundation):** autenticação via virtual key LiteLLM simples (sem Keycloak), uma key por squad
- **Fase 2 (Identity):** Keycloak + OIDC + JWT + RBAC completo

Ver roadmap em [phases-roadmap](/reference/phases-roadmap.md).

## Motivos

- Keycloak já presente na instituição — reduz overhead operacional
- OIDC/OAuth2: padrão amplo, suportado por todas ferramentas
- Device Authorization Flow: adequado para CLI (sem redirect de browser)
- JWT: stateless, verificável pelo gateway sem roundtrip ao Keycloak
- JWKS: rotação de chaves automática

## Alternativas consideradas

| Solução | Motivo descarte |
|---|---|
| API key estática por dev | Sem identidade real, sem rastreabilidade, difícil revogar |
| Auth0 / Okta | SaaS externo, dados institucionais fora do perímetro |
| Implementação própria | Complexidade de segurança desnecessária com Keycloak disponível |

## Consequências

- `tce-ai login` abre Device Authorization Flow com o Keycloak institucional
- Token armazenado em `~/.tce-ai/token.json` com renovação automática
- Revogação de acesso: feita no Keycloak, refletida imediatamente (JWT com TTL curto + refresh)
- Squads e projetos gerenciados como grupos/atributos no Keycloak

## Relacionamentos

- [security-model](/architecture/security-model.md)
- [adr-003-ai-gateway](/decisions/adr-003-ai-gateway.md)
- [rbac-roles](/reference/rbac-roles.md)
