# Log

## 2026-08-10 (institutional-fast — quota Gemini zerada, não é bug de config)

`institutional-fast` (`gemini/gemini-2.0-flash`) segue falhando com `429 RESOURCE_EXHAUSTED, limit: 0` mesmo após trocar `GEMINI_API_KEY` no `.env` e recriar o container (`docker compose up -d litellm` — confirmado via env dentro do container que a chave nova carregou). Quota 0 no tier gratuito é do **projeto Google Cloud/AI Studio por trás da chave**, não da chave em si — troca de chave sozinha não resolve se o projeto não tem billing habilitado. Ação pendente: habilitar billing no projeto ou usar chave de projeto com billing ativo. `institutional-coding` (Anthropic, sem crédito) e `institutional-reasoning` (OpenAI ✅) não são afetados.

---

## 2026-08-10 (bug crítico — "No api key passed in" ao usar tcecode)

**Sintoma:** qualquer requisição via `tcecode` (TUI ou `run`) falhava com `Authentication Error, No api key passed in.`, mesmo com virtual key configurada e válida (testada com sucesso via curl direto).

**Dois bugs empilhados, achados via debug prints temporários em `opencode/packages/opencode/src/provider/provider.ts` (`resolveSDK` e o wrapper de `fetch`):**

1. **`cli/tcecode/config.py: write_agent_config()` não setava `"npm": "@ai-sdk/openai"`** no provider `openai` do config do agente. Na branch `dev` do OpenCode (HEAD, não uma versão fixa), `v1/config/migrate.ts:migrateProvider()` usa `info.npm` pra escolher o "lowerer" que transforma `options.apiKey` em header `Authorization`; sem `npm`, cai no lowerer `raw`, que só joga `options` cru dentro do `body` — a apiKey nunca vira header. Fix: adicionar `"npm": "@ai-sdk/openai"` ao provider_cfg.
2. **`GATEWAY_URL` default era `http://localhost/v1`, não `https://`.** O Traefik redireciona `:80` → `:443` (308). Trocar de `http` pra `https` conta como troca de **origem** pro `fetch`/Bun, que **descarta o header `Authorization` em redirects cross-origin** (comportamento de segurança do próprio spec do Fetch). Mesmo com o bug 1 corrigido e o header sendo gerado certinho na primeira tentativa, ele se perdia no redirect. Fix: `GATEWAY_URL` default trocado para `https://localhost/v1` em `cli/tcecode/config.py`.

**Como validar:** `~/.tcecode/bin/tcecode-agent run "..." --model openai/<modelo>` com `NODE_TLS_REJECT_UNAUTHORIZED=0` — resposta real do modelo voltando confirma os dois fixes.

**Lição:** `tcecode configure` só salva `~/.tcecode/config.json` (config do CLI) — o config do agente (`~/.config/tcecode/config.json`, com `apiKey`/`baseURL`) só é regenerado em `tcecode login` ou no `tcecode` (sessão default). Rodar só `configure` depois de mudar `--gateway` não é suficiente.

---

## 2026-08-10 (bug crítico no viewer OKF — `</script>` no bundle quebra a página)

**Sintoma:** ao abrir `viz.html`, o grafo aparecia vazio (nenhum node) e a página mostrava um bloco enorme de texto cru (JSON escapado, `\n`, `ç`, blocos de código) no lugar da UI.

**Causa raiz:** `knowledge/development/okf-mermaid-setup.md` (trazido pelo commit remoto que adicionou suporte a Mermaid) contém, como exemplo de código, um `<script src="...mermaid.min.js"></script>` literal. O gerador do viewer (`reference_agent/viewer/generator.py`) serializa o bundle inteiro com `json.dumps(...)` e injeta direto dentro de uma tag `<script>` sem escapar `</`. O parser HTML do browser não sabe que está "dentro" de uma string JS — ele só procura a sequência literal `</script>` pra fechar a tag. Resultado: a tag fecha no meio do JSON, e tudo que vinha depois (o resto do bundle + toda a lógica do Cytoscape) vira texto solto no `<body>`.

**Fix:** `.replace("</", "<\\/")` em cima do `json.dumps(...)` no `generator.py` vendorizado (`~/.claude/skills/okf/.../viewer/generator.py`), escapando qualquer `</` antes de embutir no HTML — padrão comum para JSON-em-`<script>`. Automatizado como passo 3 de `scripts/patch-okf-mermaid.sh` (idempotente, roda junto com o patch de Mermaid).

**Lição:** qualquer concept `.md` do bundle que contenha um literal `</script>` (comum em runbooks que documentam tags HTML) quebra o viewer até esse fix ser aplicado. Vale rodar `bash scripts/patch-okf-mermaid.sh && ./viz.sh` após qualquer instalação nova da skill OKF.

---

## 2026-08-10 (instalação local — CLI + fix Traefik)

**Instalação do `tcecode` seguindo o README em ambiente novo (WSL2 + Docker Desktop 4.71, Engine 29.4.1).**

- CLI instalado via `pipx install -e cli/` (pip direto falha: ambiente `externally-managed`, PEP 668). README ainda cita `tce-ai`/`pip install -e cli/` — desatualizado, pacote real é `tcecode` (`cli/tcecode/`); `cli/tce_ai/` é órfão, não referenciado no `pyproject.toml`.
- Download do engine (release GitHub v0.1.72) retorna 404 — mesmo problema já registrado abaixo ("repo transferido"). Contornado instalando `opencode-ai` via `npm i -g` e deixando `tcecode update` vincular a instalação do sistema (fallback já implementado em `agent.py`).
- **Bug 1 — certs ausentes:** `traefik/dynamic.yaml` esperava `/certs/tce-ai.crt`/`.key`, inexistentes (gitignored, sem script de geração). Traefik subia mas sem TLS funcional. Gerados manualmente com `openssl` (ver ADR-007).
- **Bug 2 — Traefik v3.2 incompatível com Docker Engine 29.x:** provider `docker` da v3.2 usa API 1.24 fixa, rejeitada pelo Engine 29.x (mínimo 1.40+). Sintoma: `unhealthy` + loop de erro "Failed to retrieve information of the docker client and server host", nenhuma rota via label (litellm, grafana) descoberta. Corrigido subindo para `traefik:v3.6` (auto-negociação de API). ADR-007 atualizado.
- Após os dois fixes: `tcecode status` → Gateway online; `make create-squad-key SQUAD=squad-test` funcionando; `tcecode configure` + `tcecode models` retornando os 3 modelos institucionais ✅.
- **Pendência não bloqueante:** Keycloak aparece `unhealthy` no `docker compose ps`, mas os logs mostram a aplicação respondendo normalmente a tentativas de login — suspeita de healthcheck mal configurado (imagem sem `curl`/`wget`), não investigado a fundo. Afeta apenas `tcecode login` (JWT), não o fluxo de virtual key.

---

## 2026-08-10 (atualização — migração para Traefik)

**Nginx substituído por Traefik v3.2** (ADR-007). Stack 100% production-like revalidado.

- `traefik/traefik.yaml` e `traefik/dynamic.yaml` criados (roteamento, middlewares, TLS)
- Lições registradas: label conflict multi-service, replacePath middleware, SSL em urllib
- `tcecode status` corrigido para ignorar cert autoassinado (ssl.CERT_NONE)
- Fluxo validado: `tcecode status` → Gateway: online; `/v1/models` retorna 3 modelos institucionais ✅

---

## 2026-08-10

**Fase 1 — Foundation concluída e validada.**

**Implementação:**
- Stack Docker production-like subido: LiteLLM + Nginx (TLS) + Redis + Postgres + Prometheus + Grafana
- `tcecode` CLI criado como produto institucional (Python/Typer) — OpenCode gerenciado internamente como engine, invisível ao desenvolvedor
- `tcecode update` detecta e vincula instalação existente do OpenCode no sistema
- Virtual key criada para `squad-test` via `make create-squad-key`
- Fluxo end-to-end validado: `tcecode → OpenCode → Nginx → LiteLLM → OpenAI ✅`

**Decisões registradas:**
- ADR-001 atualizado: `tcecode` é o produto, não um wrapper — OpenCode é detalhe de implementação
- ADR-002 atualizado: sem fork do OpenCode nas Fases 1–4
- ADR-006 criado: limitações de branding da TUI sem fork — aceitas para Fase 1

**Problemas encontrados e resolvidos:**
- `internal: true` no Docker bloqueava egress do LiteLLM para providers externos → litellm adicionado à rede `public`
- Health check usava `curl` (ausente na imagem LiteLLM) → corrigido para `python3 urllib`
- Health endpoint `/health` exige auth no LiteLLM → nginx proxy para `/health/liveliness`
- Download do OpenCode falhou (repo transferido + urllib sem redirect handling) → `agent.py` detecta instalação existente no sistema

**Status dos providers:**
- `institutional-reasoning` → OpenAI ✅
- `institutional-coding` → Anthropic ❌ sem crédito
- `institutional-fast` → Gemini ❌ free tier esgotado

**Próxima fase:** Fase 2 — Identity (Keycloak + OIDC + JWT + RBAC)

---

## 2026-08-09

Bundle criado. Sessão de arquitetura completa. Definição e documentação de toda a plataforma institucional.

**Decisões tomadas:**
- ADR-001: Stack — Python/Typer + LiteLLM
- ADR-002: OpenCode como engine
- ADR-003: LiteLLM Proxy como AI Gateway
- ADR-004: Keycloak + OIDC para identidade (Fase 2)
- ADR-005: Multi-repo strategy
