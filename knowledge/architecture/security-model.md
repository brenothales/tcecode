---
type: Architecture Pattern
title: Modelo de Segurança da Plataforma
description: Threat model, RBAC, gestão de credenciais e políticas de segurança da AI Platform.
tags: [security, rbac, vault, credentials, threat-model]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
status: stable
---

# Modelo de Segurança da Plataforma

## Princípios

1. **Zero trust de credenciais:** desenvolvedor nunca tem acesso a API keys de provedores de IA
2. **Menor privilégio:** cada componente acessa apenas o que precisa
3. **Auditabilidade:** toda requisição tem identidade, timestamp e é registrada
4. **Segregação de segredos:** secrets em Vault/Kubernetes Secrets, nunca em código ou config versionada

---

## Fluxo de credenciais (Fase 2)

```
Vault / Kubernetes Secrets
    │  (injetado via sidecar ou env)
    ▼
LiteLLM Proxy (único componente que conhece API keys dos provedores)
    │
    │  NÃO expõe API keys para fora
    │  Expõe: virtual keys por squad (acesso ao gateway)
    ▼
OpenCode
    │  (recebe virtual key — não é API key real)
    ▼
Desenvolvedor
    (nunca vê credenciais de provedores)

Keycloak (Identity Provider)
    │  ROPC Grant → JWT (5 min) + refresh_token
    ▼
tcecode CLI
    │  JWT: identidade do desenvolvedor (quem está usando)
    │  Virtual key: credencial de acesso ao LiteLLM
    └─► ~/.tcecode/token.json  (JWT, refresh, expires_at)
        ~/.opencode/config.json (apiKey = virtual key do squad)
```

> **Nota Fase 2**: LiteLLM `enable_jwt_auth` é enterprise-only. JWT é usado para identidade
> no tcecode; acesso real ao gateway ainda via virtual key por squad. Fase 3 introduzirá
> middleware Traefik (ForwardAuth) para validar JWT e injetar virtual key automaticamente.

---

## RBAC — Papéis

| Role | Permissões |
|---|---|
| `AI_PLATFORM_ADMIN` | Gerencia todos os componentes, configura provedores, define políticas globais |
| `AI_ARCHITECT` | Define e aprova padrões arquiteturais, Skills, AGENTS.md globais |
| `AI_SQUAD_ADMIN` | Gerencia membros, quotas e políticas da própria squad |
| `AI_DEVELOPER` | Usa o agente dentro das políticas da squad e projeto |
| `AI_READONLY` | Apenas leitura de logs, métricas, documentação |
| `AI_AUDITOR` | Acesso completo a logs de auditoria, sem acesso ao agente |

Ver detalhes em [rbac-roles](/reference/rbac-roles.md).

---

## Gestão de secrets

### Fase 1 (Foundation)
- API keys dos provedores: Kubernetes Secrets no namespace `ai-platform`
- Virtual keys do LiteLLM: geradas pelo admin, distribuídas por squad via canal seguro
- Rotação manual, documentada

### Fase 2+ (com Vault)
- API keys dos provedores: HashiCorp Vault (dynamic secrets com TTL)
- Injeção via Vault Agent Sidecar no pod do LiteLLM
- Rotação automática configurável
- Audit log do Vault registra cada acesso

---

## Proibições do agente (Agent Prohibitions Policy)

O agente **não pode:**

- Acessar secrets diretamente (arquivos, env vars com credenciais)
- Criar ou modificar credenciais
- Ignorar ou desabilitar testes
- Remover mecanismos de segurança (auth, authn, rate limit)
- Remover logs de auditoria
- Alterar pipelines de produção sem revisão humana
- Copiar código proprietário de fontes externas sem licença
- Armazenar informações sensíveis no contexto da sessão
- Executar ações destrutivas (kubectl delete, DROP TABLE, restart produção) sem autorização explícita
- Introduzir dependências sem aprovação (verificar lista de dependências permitidas)

Essas proibições ficam registradas no `AGENTS.md` de cada projeto e nas Skills institucionais.

---

## Threat model — principais riscos

| Ameaça | Mitigação |
|---|---|
| Vazamento de API key via código | Developer nunca recebe API key real; virtual key com escopo limitado |
| Prompt injection via código analisado | Agente não executa código arbitrário sem sandbox; ferramentas têm escopo declarado |
| Desenvolvedor com acesso indevido a modelo | RBAC por role+squad+projeto; quota separada |
| Exfiltração de dados via LLM | Políticas de conteúdo no AGENTS.md; auditoria de todas as chamadas |
| Comprometimento do Gateway | Network Policy restrito; TLS mutual; secrets no Vault com TTL curto |
| Custo descontrolado | Quotas por desenvolvedor/squad; alertas de threshold no Grafana |
| Secrets em commits (projetos das squads) | AGENTS.md proíbe explicitamente; Skill de segurança detecta padrões perigosos |

---

## Network Policies (Kubernetes)

```
tce-ai CLI (fora do cluster)
    │  HTTPS/TLS → Ingress → litellm-proxy (ai-platform ns)
    
litellm-proxy → Anthropic/OpenAI/Gemini (saída internet controlada)
litellm-proxy → Ollama (ai-platform ns, sem saída internet)
litellm-proxy → Postgres (ai-platform ns, sem saída internet)

MCP Servers → GitLab, Jira, K8s API (redes internas permitidas)
```

---

## Relacionamentos

- [adr-004-identity](/decisions/adr-004-identity.md)
- [rbac-roles](/reference/rbac-roles.md)
- [overview](/architecture/overview.md)
