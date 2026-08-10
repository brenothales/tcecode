# Institutional AI Engineering Platform — TCE

Plataforma de engenharia de software assistida por IA para as squads do Tribunal de Contas.

## Início rápido

### 1. Subir o AI Gateway localmente

```bash
cd gateway
cp .env.example .env
# Editar .env com as API keys institucionais fornecidas pelo AI_SQUAD_ADMIN
docker compose up -d
```

### 2. Instalar o CLI

```bash
pip install -e cli/
# ou pipx install cli/
```

### 3. Instalar o OpenCode (coding agent)

```bash
tce-ai install
# Seguir as instruções para instalar o OpenCode
```

### 4. Configurar

```bash
tce-ai configure
# Squad: squad-dados
# Virtual key: (fornecida pelo AI_SQUAD_ADMIN)
```

### 5. Usar

```bash
tce-ai           # inicia sessão de coding
tce-ai models    # lista modelos disponíveis
tce-ai status    # verifica conectividade com o gateway
```

---

## Estrutura do repositório

```
tce-ai/
  gateway/          ← AI Gateway (LiteLLM)
  cli/              ← tce-ai CLI (Python)
  skills/           ← Skills institucionais por tecnologia
  knowledge/        ← OKF: arquitetura, decisões, padrões
  .okf-template/    ← Template de OKF para projetos das squads
  AGENTS.md         ← Regras institucionais para o agente neste repo
```

## Documentação arquitetural

Consulte `knowledge/index.md` para a visão completa da plataforma.

## Roadmap

Ver `knowledge/reference/phases-roadmap.md`.

| Fase | Status | Conteúdo |
|---|---|---|
| 1 — Foundation | 🚧 Em andamento | OpenCode + LiteLLM + tce-ai CLI |
| 2 — Identity | Planejada | Keycloak + OIDC + RBAC |
| 3 — Knowledge | Planejada | Skills completas + OKF integrado |
| 4 — Tools | Planejada | MCP Servers institucionais |
| 5 — Agents | Planejada | A2A: agentes especializados |
| 6 — Governance | Planejada | Audit, Cost, Quota, Compliance |
