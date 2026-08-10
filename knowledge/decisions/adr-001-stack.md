---
id: adr-001
type: Decision
title: tcecode — Produto institucional de coding agent
status: accepted
date: 2026-08-10
---

# ADR-001 — tcecode: produto institucional, não wrapper

## Contexto

A plataforma precisa de uma ferramenta que o desenvolvedor instale e use diretamente, como faria com qualquer CLI profissional. A abordagem inicial de "wrapper que lança OpenCode" foi revisada: o desenvolvedor não deve saber que existe um OpenCode por baixo. O produto institucional se chama **tcecode**.

## Decisão

- **Produto:** `tcecode` — CLI institucional instalável, o desenvolvedor nunca interage com OpenCode diretamente
- **Implementação interna:** OpenCode binary gerenciado pelo próprio `tcecode` (download, versionamento, atualização)
- **Linguagem do tcecode:** Python 3.10+, usando **Typer**
- **Distribuição:** `pipx install tcecode` (Fase 1) → Homebrew / script de instalação (Fase 3)
- **Gateway:** LiteLLM Proxy (invisível ao desenvolvedor)

## Fork do OpenCode?

**Não é necessário fork para as Fases 1–4.**

OpenCode suporta endpoint OpenAI-compatible, AGENTS.md e MCP — tudo que precisamos via configuração. O `tcecode` gerencia o binary do OpenCode internamente: baixa a versão aprovada pela plataforma, configura o gateway e lança.

Fork seria necessário apenas se quiséssemos alterar a TUI/UX do agente ou adicionar comportamentos não configuráveis. Isso é avaliado na Fase 5.

## Fluxo do desenvolvedor

```bash
# Instalar
pipx install tcecode

# Autenticar (uma vez)
tcecode login

# Usar
tcecode           # abre sessão de coding
tcecode models    # lista modelos disponíveis
tcecode status    # verifica conectividade
tcecode update    # atualiza o binary interno do agente
```

## Gerenciamento do binary interno

```
~/.tcecode/
  config.json        ← configuração do usuário
  token.json         ← JWT do Keycloak (Fase 2)
  bin/
    opencode         ← binary gerenciado pelo tcecode (não exposto ao dev)
  versions.json      ← versão aprovada pela plataforma
```

O `tcecode` baixa automaticamente a versão aprovada do OpenCode na primeira execução e verifica atualizações periodicamente.

## Motivos

- Developer Experience: um único comando para instalar e usar
- Independência de fornecedor: trocar o engine interno (OpenCode → outro) sem impacto para os devs
- Controle de versão: a plataforma aprova qual versão do engine está disponível
- Sem fork: OpenCode configurável o suficiente para as necessidades atuais

## Consequências

- `tcecode` é o único artefato que o desenvolvedor instala
- OpenCode não aparece na documentação para desenvolvedores — é detalhe de implementação
- Troca de engine no futuro: atualizar `tcecode`, transparente para os devs

## Relacionamentos

- [overview](/architecture/overview.md)
- [adr-002-coding-agent](/decisions/adr-002-coding-agent.md)
- [adr-003-ai-gateway](/decisions/adr-003-ai-gateway.md)
