---
id: adr-003
type: Decision
title: AI Gateway — LiteLLM Proxy
status: accepted
date: 2026-08-09
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
---

# ADR-003 — AI Gateway: LiteLLM Proxy

## Contexto

A plataforma precisa de um proxy entre os coding agents e os provedores de IA (Anthropic, OpenAI, Gemini, Ollama) que centralize autenticação, roteamento, rate limiting, quotas, custos e auditoria — sem que os desenvolvedores tenham acesso às API keys dos provedores.

## Decisão

**LiteLLM Proxy** é o AI Gateway da plataforma institucional.

Expõe uma API compatível com OpenAI (`POST /v1/chat/completions`) — qualquer cliente que suporte OpenAI funciona sem alteração.

## Arquitetura do Gateway

```
tce-ai / OpenCode
    │
    │  POST /v1/chat/completions
    │  Authorization: Bearer <jwt-desenvolvedor>
    ▼
LiteLLM Proxy
    ├── Auth (JWT via Keycloak — Fase 2)
    ├── RBAC (virtual keys por squad/projeto)
    ├── Model Router (institutional-coding → claude-3-5-sonnet)
    ├── Rate Limiter / Quotas
    ├── Cost Tracker
    ├── Fallback Logic
    ├── Audit Logger (OpenTelemetry)
    └── Provider Adapters
         ├── Anthropic
         ├── OpenAI
         ├── Gemini
         ├── Ollama / vLLM
         └── Azure OpenAI
```

## Modelos lógicos institucionais

```yaml
# Desenvolvedor vê apenas estes nomes:
institutional-coding     → claude-3-5-sonnet-20241022 (Anthropic)
institutional-reasoning  → o3 (OpenAI)
institutional-fast       → gemini-2.0-flash (Google)
institutional-local      → qwen2.5-coder:32b (Ollama/vLLM)
```

Ver detalhes em [logical-models](/reference/logical-models.md).

## Motivos

- API OpenAI-compatible: zero mudança no cliente (OpenCode, Cursor, VS Code Copilot, etc.)
- Suporte nativo a Anthropic, OpenAI, Gemini, Ollama, Azure, Bedrock — sem adapters customizados
- Virtual keys: cada squad/desenvolvedor tem uma chave que não é a API key real do provedor
- Rate limiting e quotas por virtual key configuráveis via YAML
- Cost tracking nativo com dashboard
- Fallback entre providers configurável por modelo lógico
- Deploy simples via Docker / Helm chart
- Licença MIT (core) / Enterprise disponível para features avançadas

## Alternativas consideradas

| Solução | Motivo descarte |
|---|---|
| Kong AI Gateway | Produto comercial, complexidade de licenciamento |
| Portkey | SaaS com opção self-hosted — menos controle, menos transparente |
| Proxy customizado | Manutenção alta, reinvenção de funcionalidades já maduras no LiteLLM |
| Acesso direto ao provedor | Viola o princípio de centralização de credenciais |

## Consequências

- LiteLLM Proxy roda em Kubernetes (namespace `ai-platform`)
- Configuração versionada em `tce-ai-gateway/` — não contém secrets, apenas referências
- Secrets dos provedores ficam em Kubernetes Secrets / Vault (ver [security-model](/architecture/security-model.md))
- Mudança de provedor: editar `litellm-config.yaml`, sem impacto nos clientes

## Relacionamentos

- [ai-gateway](/architecture/ai-gateway.md)
- [security-model](/architecture/security-model.md)
- [adr-001-stack](/decisions/adr-001-stack.md)
- [adr-004-identity](/decisions/adr-004-identity.md)
- [logical-models](/reference/logical-models.md)
