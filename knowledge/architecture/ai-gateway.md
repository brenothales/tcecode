---
type: Architecture Pattern
title: AI Gateway — Design Detalhado
description: Arquitetura interna do LiteLLM Proxy como gateway institucional de IA.
tags: [gateway, litellm, routing, auth, observability]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
status: stable
---

# AI Gateway — Design Detalhado

## Responsabilidades

| Função | O que faz |
|---|---|
| **Auth** | Valida JWT do Keycloak (Fase 2) ou virtual key (Fase 1) |
| **RBAC** | Verifica se o role do usuário pode usar o modelo solicitado |
| **Routing** | Traduz modelo lógico (`institutional-coding`) para modelo real (`claude-3-5-sonnet`) |
| **Rate Limit** | Limita req/min por virtual key / squad |
| **Quotas** | Limita tokens/dia por desenvolvedor e squad |
| **Cost Tracking** | Calcula custo estimado por token e agrega por squad/projeto |
| **Fallback** | Se provedor principal falhar, tenta o próximo configurado |
| **Audit** | Registra toda requisição com user, squad, model, tokens, latência |
| **Observability** | Exporta métricas para Prometheus, traces para OpenTelemetry |

---

## Modelo lógico de roteamento

```yaml
# litellm-config.yaml (sem secrets — secrets em Kubernetes Secrets / Vault)

model_list:
  - model_name: institutional-coding
    litellm_params:
      model: anthropic/claude-3-5-sonnet-20241022
      api_key: os.environ/ANTHROPIC_API_KEY
    model_info:
      description: "Modelo primário para coding — alta qualidade"

  - model_name: institutional-reasoning
    litellm_params:
      model: openai/o3
      api_key: os.environ/OPENAI_API_KEY

  - model_name: institutional-fast
    litellm_params:
      model: gemini/gemini-2.0-flash
      api_key: os.environ/GEMINI_API_KEY

  - model_name: institutional-local
    litellm_params:
      model: ollama/qwen2.5-coder:32b
      api_base: http://ollama.tce.internal:11434

router_settings:
  routing_strategy: usage-based-routing
  fallbacks:
    - institutional-coding:
        - institutional-fast
        - institutional-local
```

---

## Fallback strategy

```
Requisição → institutional-coding
                    │
                    ▼
              Claude 3.5 Sonnet
                    │
               timeout / error
                    │
                    ▼
              Gemini 2.0 Flash
                    │
               timeout / error
                    │
                    ▼
         Qwen 2.5 Coder (local)
```

Configurável por modelo lógico — sem impacto no cliente.

---

## Quotas e limites

```yaml
litellm_settings:
  callbacks: ["prometheus", "otel"]

general_settings:
  database_url: os.environ/DATABASE_URL  # PostgreSQL para persistência de quotas

# Configurado via API de admin do LiteLLM:
# POST /team/new  (squad)
# POST /key/generate  (virtual key por desenvolvedor)
# Quota de tokens configurada por squad e por desenvolvedor
```

---

## Observabilidade do Gateway

Métricas expostas em `/metrics` (Prometheus):

```
litellm_requests_total{model, provider, squad, status}
litellm_tokens_total{model, provider, squad, type="input|output"}
litellm_latency_seconds{model, provider, squad}
litellm_cost_total{model, provider, squad}
litellm_errors_total{model, provider, error_type}
```

Nunca registrar: conteúdo das mensagens, API keys, tokens de acesso.

---

## Deploy Kubernetes

```
namespace: ai-platform
  deployment: litellm-proxy
  service: litellm-proxy (ClusterIP)
  ingress: ai-gateway.tce.internal (TLS)
  secret: ai-providers-keys (Vault injected)
  configmap: litellm-config (sem secrets)
  hpa: min=2, max=8 (baseado em CPU/req)
```

---

## Relacionamentos

- [adr-003-ai-gateway](/decisions/adr-003-ai-gateway.md)
- [security-model](/architecture/security-model.md)
- [logical-models](/reference/logical-models.md)
