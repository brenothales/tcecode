---
type: Architecture Pattern
title: Multi-Agent Architecture (A2A)
description: Arquitetura de agentes especializados acionados via A2A pelo coding agent principal.
tags: [a2a, agents, specialized, architecture, security, devops]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
status: draft
---

# Multi-Agent Architecture (A2A)

> Fase 5 do roadmap. Esta documentação registra a arquitetura planejada para evoluir a partir dos componentes da Fase 1-4.

## Conceito

O coding agent principal (OpenCode) pode acionar agentes especializados para tarefas que exigem expertise específica. Cada agente tem responsabilidade clara, skill set, ferramentas e permissões próprias.

## Hierarquia de agentes

```
Desenvolvedor
    │
    ▼
TCE Coding Agent (OpenCode + AGENTS.md institucional)
    │
    ├── Architecture Agent   ← quando mudança arquitetural é detectada
    ├── Security Agent       ← quando código suspeito é gerado
    ├── DevOps Agent         ← quando deploy/infra é necessário
    ├── Database Agent       ← quando schema/query crítica é alterada
    ├── Testing Agent        ← quando cobertura insuficiente é detectada
    └── Documentation Agent  ← quando ADR/OKF precisa ser atualizado
```

## Contrato de cada agente

Cada agente expõe:

```yaml
# agent-card.yaml
id: security-agent
name: "TCE Security Agent"
version: "1.0.0"
description: "Analisa código em busca de vulnerabilidades de segurança"
capabilities:
  - code_review
  - owasp_analysis
  - secret_detection
  - dependency_audit
tools:
  - read_file
  - search
  - run_sast
input_schema:
  files: list[string]
  context: string
output_schema:
  findings: list[Finding]
  severity: "critical|high|medium|low"
  approved: boolean
permissions:
  - read_project_files
  - run_static_analysis
prohibited:
  - write_files
  - execute_commands
  - access_production
```

## Padrão de comunicação A2A

```
Coding Agent
    │
    │  POST /a2a/security-agent/analyze
    │  {files: [...], context: "implementei novo endpoint de login"}
    ▼
Security Agent
    │  analisa
    ▼
    │  {findings: [...], approved: false, reason: "SQL injection em UserRepository.java:42"}
    ▼
Coding Agent
    │  apresenta ao desenvolvedor e bloqueia commit se crítico
```

## Princípios de design

- **Responsabilidade única:** cada agente faz uma coisa bem
- **Permissões mínimas:** agente de leitura não escreve, agente de análise não executa
- **Observabilidade:** cada chamada A2A gera trace correlacionado com a sessão principal
- **Idempotência:** análises repetidas produzem o mesmo resultado
- **Timeout:** toda chamada A2A tem timeout configurado (agentes não bloqueiam indefinidamente)

## Relacionamentos

- [overview](/architecture/overview.md)
- [tce-agent](/agents/tce-agent.md)
- [phases-roadmap](/reference/phases-roadmap.md)
