---
type: Decision
title: ADR-010 — Distribuição via instalador one-liner (build local)
description: curl/irm | bash/iex para instalar o tcecode — clona o repo institucional e builda o fork localmente, sem CI de binários.
tags: [install, distribution, bitbucket, cross-platform]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-11T00:00:00Z"
status: stable
---

# ADR-010 — Distribuição via instalador one-liner

## Status

Implementado em 2026-08-11. Substitui uma primeira versão que publicava binários pré-buildados via Bitbucket Pipelines + Downloads (descartada antes de ir para produção — ver seção "Alternativa descartada").

## Contexto

Até aqui, instalar o `tcecode` exigia passos manuais: `pipx install -e cli/`, clonar o fork do OpenCode, instalar Bun, buildar localmente. Isso não escala para squads inteiras sem documentação. O padrão de mercado é um instalador one-liner (`curl -fsSL <url>/install | bash`, como o próprio `opencode.ai` usa).

O repositório institucional vive no Bitbucket (`git@bitbucket.org:tcesc-git/tcecode.git`). O `cli/tcecode/agent.py` resolve o caminho do fork buildado (`_FORK_BIN`) **relativo ao próprio clone do repositório** (`Path(__file__).parent.parent.parent / "opencode" / ...`) — isso só funciona com uma instalação editável (`pipx install -e`) a partir de um clone persistente, não com um pacote solto instalado via pip/PyPI.

## Decisão

**`scripts/install.sh`** (Linux/macOS) e **`scripts/install.ps1`** (Windows) fazem tudo localmente, sem depender de nenhum artefato pré-buildado:

1. Clonam (ou atualizam) o repo `tcecode` em `~/.local/share/tcecode-src` (Linux/macOS) ou `%LOCALAPPDATA%\tcecode-src` (Windows).
2. Clonam o fork `brenothales/opencode` (branch `dev`) dentro desse clone, em `opencode/` — path esperado pelo `agent.py`.
3. Instalam Bun se necessário, buildam o `tcecode-agent` (`bun run script/build.ts --single --skip-embed-web-ui`).
4. Instalam o CLI via `pipx install -e <clone>/cli` (editável, pra manter a resolução de path do fork funcionando).
5. Rodam `tcecode update`, que já encontra o binário buildado em `_FORK_BIN` e vincula.

Preferem SSH (`git@bitbucket.org`) quando configurado, caem para HTTPS com aviso caso contrário — mesma lógica para o fork no GitHub.

## Alternativa descartada: binários pré-buildados via CI

Uma primeira versão publicava binários pré-buildados (Bitbucket Pipelines, disparado em tags `agent-v*`, build cross-platform via `bun build --compile`, upload para Bitbucket Downloads via Repository Access Token). Descartada porque:

- Adicionava uma peça de infra extra (pipeline + token + variável secured) para um ganho que não valia a complexidade neste estágio do projeto — o objetivo era o dev rodar um comando, não manter um pipeline de release.
- O build local (~2-3 min, majoritariamente `bun install`) é aceitável para instalação única por máquina.

Se o tempo de build virar um problema real (squads grandes, máquinas lentas), vale reconsiderar — o pipeline descartado fica como referência no histórico do git (commit anterior a este ADR).

## Consequências

**Positivo:**
- Instalação de squad inteira em um comando, sem passos manuais documentados à parte.
- Sem infraestrutura de CI/credenciais extra para manter.

**Trade-offs / pendências:**
- **Repositório privado**: se `tcesc-git/tcecode` não for público, `git clone`/`pipx install` exigem credenciais (SSH configurado ou HTTPS com prompt). Os scripts tentam SSH primeiro e avisam se cair para HTTPS.
- **Tempo de instalação**: build local do fork (~2-3 min na primeira vez, incluindo `bun install` do monorepo inteiro) — não é instantâneo como baixar um binário pronto.
- **Windows nativo**: `AGENT_BIN` em `config.py` não distingue `.exe`; suporte Windows do `tcecode` CLI em si é best-effort, não validado numa máquina Windows real.
- **Não testado**: scripts escritos e revisados, mas não executados de ponta a ponta numa máquina limpa nem no Bitbucket institucional real.

## Referências

- [cli/tcecode/agent.py](/cli/tcecode/agent.py)
- [scripts/install.sh](/scripts/install.sh)
- [scripts/install.ps1](/scripts/install.ps1)
- [adr-009-fork-opencode](/decisions/adr-009-fork-opencode.md)
