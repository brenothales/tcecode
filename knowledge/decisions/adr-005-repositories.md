---
id: adr-005
type: Decision
title: Estratégia de Repositórios — Multi-repo
status: accepted
date: 2026-08-09
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-09T00:00:00Z"
---

# ADR-005 — Estratégia de Repositórios: Multi-repo

## Contexto

A plataforma é composta por componentes com ciclos de vida, times responsáveis e frequências de deploy distintos. A escolha entre monorepo e multi-repo impacta autonomia das squads, governança e operação do CI/CD.

## Decisão

**Multi-repo** com um repositório por componente principal da plataforma.

```
tce-ai-platform/    # Documentação, visão geral, ADRs globais (este repo)
tce-ai-gateway/     # LiteLLM config + Kubernetes manifests
tce-ai-cli/         # tce-ai Python wrapper + OpenCode distribution
tce-ai-skills/      # Skills institucionais (SKILL.md por tecnologia)
tce-ai-agents/      # Definições dos agentes especializados (A2A)
tce-ai-mcp/         # MCP servers institucionais
tce-ai-templates/   # Templates de novos projetos (Spring Boot, etc.)
tce-ai-policies/    # Governance policies (JSON/YAML)
```

## Motivos

### Multi-repo é adequado porque

- Componentes têm times e proprietários distintos (equipe de plataforma ≠ equipe de skills)
- Ciclos de deploy independentes: gateway muda raramente, skills mudam frequentemente
- Permissões granulares por repositório — RBAC de contribuição separado por componente
- Clone leve: desenvolvedor clona apenas o que precisa
- Histórico limpo por componente — não há ruído de commits de outros componentes

### Monorepo descartado porque

- Tooling de monorepo (Nx, Turborepo, Bazel) adiciona overhead de configuração sem ganho claro aqui
- Componentes são em linguagens diferentes (Python, YAML, Markdown, Go futuro) — monorepo complica CI
- Políticas de acesso mais difíceis de segmentar (skills devem ser contribuíveis por todas as squads)

## Estrutura de cada repositório

```
tce-ai-<componente>/
  knowledge/          # OKF do componente
  src/ ou config/     # Código/config principal
  docs/               # Documentação operacional
  AGENTS.md           # Regras para o agente neste repo
  README.md
  .gitignore
  CI/CD pipeline
```

## Versioning entre repositórios

- `tce-ai-platform/` mantém uma matrix de versões compatíveis entre componentes
- CLI especifica a versão mínima do gateway suportada
- Skills são versionadas semanticamente e distribuídas via URL no `tce-ai-cli`

## Consequências

- Navegação requer conhecer qual repo editar — mitigado pelo `tce-ai-platform` como mapa central
- Mudanças que afetam múltiplos componentes exigem PRs em múltiplos repos — aceito como trade-off de isolamento

## Relacionamentos

- [overview](/architecture/overview.md)
- [adr-001-stack](/decisions/adr-001-stack.md)
