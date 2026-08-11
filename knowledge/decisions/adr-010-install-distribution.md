---
type: Decision
title: ADR-010 — Distribuição via instalador one-liner (Bitbucket Downloads)
description: curl/irm | bash/iex para instalar o tcecode, binário do fork publicado via Bitbucket Pipelines.
tags: [install, distribution, bitbucket, ci, cross-platform]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-11T00:00:00Z"
status: draft
---

# ADR-010 — Distribuição via instalador one-liner

## Status

Draft — implementado, pendente de configuração de credenciais no Bitbucket e validação real do pipeline (não executável a partir deste ambiente de desenvolvimento).

## Contexto

Até aqui, instalar o `tcecode` exigia passos manuais: `pipx install -e cli/`, clonar o fork do OpenCode, instalar Bun, buildar localmente (~3 min). Isso não escala para squads inteiras. O padrão de mercado é um instalador one-liner (`curl -fsSL <url>/install | bash`, como o próprio `opencode.ai` usa).

O repositório institucional vive no Bitbucket (`git@bitbucket.org:tcesc-git/tcecode.git`), não GitHub — os repos `brenothales/tcecode` e `brenothales/opencode` no GitHub são espelhos pessoais usados durante o desenvolvimento inicial. O download de release do GitHub (`sst/opencode`) já estava quebrado (404) antes desta decisão — ver `log.md`.

## Decisão

1. **`bitbucket-pipelines.yml`**: pipeline disparado em tags `agent-v*`, builda o `tcecode-agent` para todas as plataformas (Linux/macOS/Windows, x64/arm64) num único runner Linux via `bun build --compile` (cross-compile nativo do Bun, sem precisar de macOS/Windows reais), empacota cada binário e publica no **Bitbucket Downloads** do repo via API REST.
2. **`cli/tcecode/agent.py`**: `install_agent()` passa a baixar de `https://bitbucket.org/tcesc-git/tcecode/downloads/opencode-<os>-<arch>.tar.gz` (nome fixo por plataforma, sobrescrito a cada publish) em vez do release quebrado do GitHub.
3. **`scripts/install.sh`** (Linux/macOS) e **`scripts/install.ps1`** (Windows): instalam pipx se necessário, instalam o CLI direto do Bitbucket via `pipx install git+ssh://.../tcecode.git#subdirectory=cli`, e rodam `tcecode update` para baixar o engine.

## Consequências

**Positivo:**
- Instalação de squad inteira em um comando, sem precisar de Bun/clone manual do fork.
- `bun build --compile` cross-platform elimina a necessidade de runners macOS/Windows no CI.

**Trade-offs / pendências:**
- **Repositório privado**: se `tcesc-git/tcecode` não for público, tanto o `pipx install` quanto o `curl`/`tcecode update` exigem credenciais (chave SSH configurada ou App Password via `.netrc`) — não é um one-liner 100% anônimo. Os scripts tentam SSH primeiro e avisam se cair para HTTPS.
- **Credenciais do pipeline**: `BB_DOWNLOADS_USER` e `BB_DOWNLOADS_APP_PASSWORD` (App Password com escopo "Repositories: Write") precisam ser configuradas manualmente em Repository settings → Repository variables. Não configurado neste momento.
- **Não testado**: este ambiente de desenvolvimento não tem acesso ao Bitbucket institucional para rodar o pipeline de verdade. Validar na primeira tag `agent-v0.1.0`.
- **Windows nativo**: `AGENT_BIN` em `config.py` não distingue `.exe`; suporte Windows do `tcecode` CLI em si é best-effort, não validado.
- **Fork ainda no GitHub**: o pipeline clona `brenothales/opencode` via HTTPS público do GitHub como fonte de build. Se o fork migrar para o Bitbucket institucional, atualizar a URL de clone no `bitbucket-pipelines.yml`.

## Referências

- [bitbucket-pipelines.yml](/bitbucket-pipelines.yml)
- [cli/tcecode/agent.py](/cli/tcecode/agent.py)
- [scripts/install.sh](/scripts/install.sh)
- [scripts/install.ps1](/scripts/install.ps1)
- [adr-009-fork-opencode](/decisions/adr-009-fork-opencode.md)
