---
id: rbac-roles
type: Architecture Pattern
title: RBAC — Papéis e Permissões
status: active
---

# RBAC — Papéis e Permissões

## Papéis institucionais

### `AI_PLATFORM_ADMIN`
Equipe de plataforma. Acesso total.

- Configura provedores de IA e API keys (via Vault/K8s Secrets)
- Define modelos lógicos e roteamento
- Define políticas globais (quotas máximas, modelos proibidos)
- Gerencia roles de todos os usuários
- Acessa todos os logs de auditoria
- Deploy do AI Gateway, CLI, Skills, MCP Servers

### `AI_ARCHITECT`
Arquitetos de software. Foco em padrões e governança técnica.

- Define e aprova Skills institucionais
- Define e aprova AGENTS.md globais e por squad
- Valida ADRs de squads
- Usa todos os modelos lógicos
- Acessa dashboards de observabilidade (sem dados de conteúdo)

### `AI_SQUAD_ADMIN`
Tech lead / squad lead. Gerencia a própria squad.

- Adiciona/remove membros da squad
- Configura quotas de tokens por desenvolvedor da squad (dentro do limite global)
- Define modelo padrão da squad
- Aprova Skills específicas da squad
- Acessa métricas de uso da squad

### `AI_DEVELOPER`
Desenvolvedor. Uso do agente dentro das políticas.

- Executa `tce-ai` no terminal
- Usa modelos `institutional-coding`, `institutional-fast`, `institutional-local`
- Acessa ferramentas MCP permitidas pela squad
- Vê apenas métricas do próprio uso

### `AI_READONLY`
Observadores, auditores técnicos.

- Acessa documentação, Skills, AGENTS.md (leitura)
- Vê dashboards de métricas agregadas (sem dados individuais)
- Não executa o agente

### `AI_AUDITOR`
Auditoria e compliance.

- Acessa logs de auditoria completos (usuário, squad, modelo, timestamp, tokens)
- Sem acesso ao conteúdo das mensagens (privacidade)
- Gera relatórios de conformidade
- Não executa o agente

---

## Hierarquia de contexto (claim JWT)

```json
{
  "sub": "developer@tce.gov.br",
  "roles": ["AI_DEVELOPER"],
  "squad": "squad-dados",
  "project": "sistema-ged",
  "team_daily_token_limit": 1000000,
  "user_daily_token_limit": 100000
}
```

---

## Matriz de permissões por modelo

| Modelo | DEVELOPER | SQUAD_ADMIN | ARCHITECT | ADMIN |
|---|---|---|---|---|
| institutional-coding | ✅ | ✅ | ✅ | ✅ |
| institutional-fast | ✅ | ✅ | ✅ | ✅ |
| institutional-local | ✅ | ✅ | ✅ | ✅ |
| institutional-reasoning | ❌ | ✅ | ✅ | ✅ |

---

## Relacionamentos

- [security-model](/architecture/security-model.md)
- [adr-004-identity](/decisions/adr-004-identity.md)
