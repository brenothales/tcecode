---
type: Decision
title: ADR-009 — Fork do OpenCode como tcecode-agent
description: Fork thin do OpenCode para branding institucional completo do tcecode.
tags: [fork, opencode, branding, tui, build, bun]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-10T12:00:00Z"
status: stable
---

# ADR-009 — Fork do OpenCode: tcecode-agent

## Status
Implementado e validado em 2026-08-10. Supersede ADR-002 e ADR-006.

## Contexto

ADR-002 (sem fork) e ADR-006 (aceitar limitações de branding) foram adotados inicialmente porque o custo de manutenção do fork parecia alto. Após validação técnica, o fork se mostrou viável com mudanças mínimas:
- OpenCode é um monorepo TypeScript/Bun, não Go
- Build local demora ~1 min (Bun compile, `--single --skip-embed-web-ui`)
- Apenas 3–4 arquivos precisam de mudança para branding completo

Problemas que motivaram a mudança:
- Logo "opencode" aparecia na splash e no epilogue (tela de saída)
- `opencode -s <id>` no epilogue confunde o desenvolvedor
- Dialog de auto-update do upstream aparecia (v1.18.16 disponível) e falhava ao baixar

## Decisão

**Fork thin do OpenCode** com patches mínimos de branding. O repositório `brenothales/opencode` (branch `dev`) é o upstream do fork.

### Arquivos alterados no fork

| Arquivo | Mudança |
|---|---|
| `packages/core/src/global.ts` | `const app = "tcecode"` → XDG dirs em `~/.config/tcecode/`, `~/.local/share/tcecode/` |
| `packages/tui/src/logo.ts` | ASCII art "TCE CODE" no lugar de "opencode" |
| `packages/tui/src/util/presentation.ts` | Logo + `tcecode -s` no epilogue (tela de saída) |
| `packages/opencode/script/build.ts` | `outfile = tcecode-agent`, user-agent atualizado |

### Build

```bash
cd opencode/packages/opencode
bun run script/build.ts --single --skip-embed-web-ui
# Output: dist/opencode-darwin-arm64/bin/tcecode-agent (~102MB, arm64)
```

### Integração com tcecode CLI

- `cli/tcecode/config.py`: `AGENT_BIN = ~/.tcecode/bin/tcecode-agent`
- `cli/tcecode/config.py`: `write_agent_config` escreve em `~/.config/tcecode/config.json` (XDG do fork)
- `cli/tcecode/agent.py`: detecta binário do fork em `opencode/packages/opencode/dist/<platform>/bin/tcecode-agent`
- `cli/tcecode/main.py`: `OPENCODE_DISABLE_AUTOUPDATE=1` no env do subprocess

### Logo TCE CODE

```
left:  "████ █▀▀▀ █▀▀▀     "   (T  C  E  )
       "_██_ █___ ████     "
       "_▀▀_ ▀▀▀▀ ▀▀▀▀     "
right: "█▀▀▀ █▀▀█ █▀▀█ █▀▀█"   (C  O  D  E)
       "█___ █__█ █__█ █^^^"
       "▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀"
```

## Lições aprendidas

### 1. Renomear o package `name` quebra workspace

Alterar `"name": "opencode"` → `"name": "tcecode-agent"` em `packages/opencode/package.json` quebra todas as referências `opencode@workspace:*` no monorepo. O nome do package é interno — não alterar. Só o `outfile` do build precisa mudar.

### 2. Logo aparece em dois lugares independentes

- `packages/tui/src/logo.ts` → splash screen (tela inicial da TUI)
- `packages/tui/src/util/presentation.ts` → epilogue (tela de saída após Esc)

Ambos têm a logo hardcoded e precisam ser atualizados separadamente.

### 3. Auto-update desabilitado via env var

`OPENCODE_DISABLE_AUTOUPDATE=1` injeta no subprocess do `tcecode`. Não precisa alterar código do fork — a flag já existe no OpenCode.

### 4. XDG config separado

Com `app = "tcecode"` em `global.ts`, o fork usa `~/.config/tcecode/` independente do OpenCode original (`~/.config/opencode/`). Usuários que tinham OpenCode instalado não têm conflito de config.

## Consequências

**Positivo:**
- Identidade institucional completa: logo TCE CODE na splash e no epilogue
- `tcecode -s <id>` no epilogue (não `opencode -s`)
- Sem dialog de auto-update do upstream
- Config em `~/.config/tcecode/` separado do OpenCode original
- Build ~1 min — ciclo de iteração rápido

**Trade-offs:**
- Custo de manutenção: atualizações do upstream (sst/opencode) precisam ser mergeadas periodicamente
- Build local necessário para distribuição — sem binário pré-compilado no repositório
- Bun 1.3.14+ necessário para build (`packageManager` no root `package.json`)

## Referências

- [opencode/packages/core/src/global.ts](/opencode/packages/core/src/global.ts)
- [opencode/packages/tui/src/logo.ts](/opencode/packages/tui/src/logo.ts)
- [opencode/packages/tui/src/util/presentation.ts](/opencode/packages/tui/src/util/presentation.ts)
- [opencode/packages/opencode/script/build.ts](/opencode/packages/opencode/script/build.ts)
- [cli/tcecode/agent.py](/cli/tcecode/agent.py)
- [cli/tcecode/config.py](/cli/tcecode/config.py)
- [adr-002-coding-agent.md](/knowledge/decisions/adr-002-coding-agent.md) (supersedido)
- [adr-006-branding.md](/knowledge/decisions/adr-006-branding.md) (supersedido)
