---
type: Decision
title: ADR-008 — Fase 2 Identity — Keycloak + OIDC + Password Grant
description: Implementação da autenticação institucional via Keycloak com tcecode login.
tags: [identity, keycloak, oidc, jwt, auth, phase2]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-10T05:00:00Z"
status: stable
---

# ADR-008 — Fase 2: Identity — Keycloak + OIDC

## Status
Implementado e validado em 2026-08-10.

## Contexto

Na Fase 1, desenvolvedores recebiam virtual keys estáticas por squad (distribuição manual, sem rastreabilidade individual). A Fase 2 introduz identidade real via Keycloak: cada desenvolvedor autentica com suas credenciais institucionais e recebe um JWT pessoal.

## Decisão

**Keycloak 26.0** como Identity Provider, integrado via OIDC/OAuth2 **Resource Owner Password Credentials (ROPC) Grant**.

### Stack

| Componente | Responsabilidade |
|---|---|
| `postgres-keycloak` | DB dedicado do Keycloak (separado do LiteLLM) |
| `keycloak:26.0` | Identity Provider — realm `tce-ai`, cliente `tcecode-cli` |
| Traefik file provider | Roteamento `/auth/*` via `dynamic.yaml` (não Docker labels) |
| LiteLLM `litellm_jwtauth` | Valida JWT via JWKS do Keycloak (PENDENTE — ver lições) |

### Roteamento Traefik para Keycloak

Configurado em `dynamic.yaml` (não em Docker labels) — Traefik não detectou os labels do Keycloak corretamente neste ambiente Docker Desktop/Mac.

```yaml
routers:
  keycloak-oidc:     # OIDC protocol endpoints — público
    rule: PathPrefix('/auth/realms/tce-ai/protocol')
    priority: 50
    middlewares: [rate-limit]
  keycloak-admin:    # Admin console — interno
    rule: PathPrefix('/auth')
    priority: 40
    middlewares: [internal-only]
services:
  keycloak:
    url: http://keycloak:8080
```

### Fluxo de autenticação

```
tcecode login (--username --password)
    │
    ▼
POST /auth/realms/tce-ai/protocol/openid-connect/token
    │  grant_type=password, client_id=tcecode-cli
    ▼
Keycloak valida credenciais → emite JWT (5min) + refresh_token
    │
    ▼
~/.tcecode/token.json (JWT + refresh_token + expires_at)
    │
    ▼
tcecode → write_agent_config() → ~/.opencode/config.json (apiKey=JWT)
    │
    ▼
OpenCode → Bearer JWT → LiteLLM → provider
```

### JWT emitido pelo Keycloak

```json
{
  "preferred_username": "dev-test",
  "squad": "squad-test",
  "realm_access": { "roles": ["AI_DEVELOPER"] },
  "exp": ...
}
```

## Lições aprendidas

### 1. Traefik Docker labels ignorados no Docker Desktop/Mac

Traefik não registrou os routers do Keycloak via Docker labels mesmo com `traefik.enable=true`. O provider file (`dynamic.yaml`) funcionou imediatamente. **Regra**: para serviços estáticos de infra (Keycloak, Grafana), prefer file provider. Docker labels são adequados para serviços dinâmicos (LiteLLM).

### 2. `oauth2DeviceAuthorizationGrantEnabled` removido no Keycloak 26

O campo `oauth2DeviceAuthorizationGrantEnabled` não existe no `ClientRepresentation` do Keycloak 26.0.8 (apenas 44 campos conhecidos). O Device Authorization Grant (RFC 8628) não está acessível de forma simples via REST API nesta versão.

**Solução**: usar Resource Owner Password Credentials Grant (`directAccessGrantsEnabled: true`), adequado para ferramentas CLI internas em rede corporativa. Device Flow pode ser reativado em versão futura do Keycloak ou via Client Policies.

### 3. hot-reload do Traefik via bind mount no Docker Desktop

Editar arquivos do file provider em macOS + Docker Desktop não dispara hot-reload dentro do container (inotify não propaga via gRPC/FUSE). **Solução**: restart do Traefik após mudanças no `dynamic.yaml`.

### 4. LiteLLM `litellm_jwtauth` é enterprise-only

Após investigação completa (`enable_jwt_auth: true` + `issuers: [JWTIssuerConfig]`), o LiteLLM retornou:
> *"JWT Auth is an enterprise only feature."*

O campo correto é `issuers` (lista de `JWTIssuerConfig`, não strings), e `enable_jwt_auth: true` é obrigatório — ambos enterprise. `jwks_url` não é campo válido no nível raiz; pertence ao `JWTIssuerConfig`.

**Decisão**: separar responsabilidades:
- **JWT** = identidade do desenvolvedor no `tcecode` (quem está usando, rastreabilidade)
- **Virtual key** = credencial de acesso ao LiteLLM (por squad, Fase 1)
- OpenCode recebe virtual key; JWT fica no `tcecode` para exibição e futuro uso em middleware

**Caminho futuro para Fase 3**: middleware Traefik (Lua/ForwardAuth) que valida JWT via JWKS e injeta virtual key do squad correspondente — elimina necessidade de licença enterprise.

### 5. `tcecode models` busca modelos reais do gateway

Comando atualizado para `GET /v1/models` com virtual key em vez de tabela hardcoded. Retorna exatamente os modelos configurados no LiteLLM.

## Consequências

**Positivo:**
- Desenvolvedor autentica com credencial institucional única
- JWT contém `squad` + `roles` — base para RBAC na Fase 3
- Refresh automático de token no `tcecode` (30s buffer)
- Keycloak admin acessível em `https://localhost/auth/admin/` (rede interna)
- `tcecode models` dinâmico — lista modelos reais do gateway
- Usuário de teste: `dev-test` / `«REDACTED»` / squad: `squad-test` / role: `AI_DEVELOPER`

**Trade-offs:**
- ROPC (password grant) envia credenciais ao cliente — adequado para rede institucional interna
- Device Flow seria mais seguro mas não disponível no Keycloak 26.0.8 sem configuração adicional
- JWT não valida diretamente no LiteLLM (enterprise-only); virtual key por squad continua como acesso real ao gateway

## Referências

- [gateway/keycloak/realm-tce-ai.json](/gateway/keycloak/realm-tce-ai.json)
- [gateway/traefik/dynamic.yaml](/gateway/traefik/dynamic.yaml)
- [gateway/litellm-config.yaml](/gateway/litellm-config.yaml)
- [cli/tcecode/auth.py](/cli/tcecode/auth.py)
- [adr-004-identity.md](/knowledge/decisions/adr-004-identity.md)
