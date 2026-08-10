---
type: Decision
title: ADR-007 — Traefik como Reverse Proxy (substituindo Nginx)
description: Troca do Nginx pelo Traefik (atualmente v3.6) como reverse proxy do AI Gateway.
tags: [gateway, infra, traefik, nginx, proxy]
generated:
  by: "claude-code/sonnet-4-6"
  at: "2026-08-10T04:00:00Z"
status: stable
---

# ADR-007 — Traefik como Reverse Proxy

## Status
Aceito — implementado e validado em 2026-08-10.

## Contexto

O AI Gateway usava Nginx como reverse proxy. Durante a fase 1 surgiram problemas operacionais recorrentes com regex no Nginx (`location` com anchor `$` em grupo de alternância causava parse error), e a configuração de roteamento dinâmico para futuros módulos (Keycloak, novos serviços) exigiria manutenção de blocos de config estáticos.

Adicionalmente, o caminho de migração para Kubernetes (planejado para a fase de escala) é muito mais direto com Traefik (IngressRoute/CRD nativos) do que com Nginx (Ingress básico + anotações).

## Decisão

Substituir Nginx por **Traefik** (v3.2 na implementação inicial, **v3.6** desde 2026-08-10 — ver lição abaixo) como reverse proxy único.

Configuração dividida em dois arquivos:
- `traefik/traefik.yaml` — config estática: entrypoints (80→redirect, 443), providers (docker + file), dashboard
- `traefik/dynamic.yaml` — config dinâmica: middlewares (`rate-limit`, `internal-only`, `secure-headers`, `health-rewrite`), TLS store

Roteamento via **Docker labels** no `docker-compose.yaml`. Cada rota tem prioridade explícita:

| Prioridade | Rota | Middleware |
|---|---|---|
| 30 | `/health` (exato) | `health-rewrite@file` → `/health/liveliness` |
| 20 | `/v1/key\|team\|user\|spend\|model` (admin) | `internal-only@file` (IP allowlist) |
| 10 | `/v1/` (API pública) | `rate-limit@file`, `secure-headers@file` |
| 1  | `/` (catch-all admin) | `internal-only@file` |

**Lição aprendida (label conflict):** Quando um container expõe múltiplos services Traefik (ex.: `litellm` + `litellm-health-svc`), todos os routers precisam declarar `.service=<nome>` explicitamente — caso contrário Traefik não consegue fazer auto-link e descarta os routers silenciosamente (log: `"Router X cannot be linked automatically with multiple Services"`).

**Lição aprendida (replacePath):** Para reescrever path (ex.: `/health` → `/health/liveliness`), usar middleware `replacePath` no `dynamic.yaml`, não `stripprefix` nem `server.url` em label (inválido no Traefik v3).

**Lição aprendida (SSL em tcecode status):** O comando `tcecode status` usa `urllib.request.urlopen` que verifica certificado por padrão. Com certs autoassinados (dev), é necessário criar um `ssl.SSLContext` com `CERT_NONE` — equivalente ao `-k` do curl.

**Lição aprendida (certs ausentes):** `traefik/dynamic.yaml` referencia `/certs/tce-ai.crt` e `/certs/tce-ai.key`, mas esses arquivos não são versionados (`.gitignore`) e não há script/target automatizado para gerá-los. Em setup novo, o Traefik sobe mas falha ao criar o certificate store (`"failed to load X509 key pair: tls: failed to find any PEM data"`) e a entrypoint `websecure` fica sem TLS funcional. Gerar manualmente com `openssl req -x509 -nodes -newkey rsa:2048 -days 825 -keyout tce-ai.key -out tce-ai.crt -subj "/CN=localhost/O=TCE Code (dev)" -addext "subjectAltName=DNS:localhost,DNS:traefik.localhost,DNS:*.localhost,IP:127.0.0.1"` dentro de `gateway/traefik/`. Vale automatizar isso como target `make gen-certs`.

**Lição aprendida (Docker API 1.24 vs Docker Engine 29.x):** `traefik:v3.2` embute um client Docker SDK que usa a API version 1.24 por padrão para o provider `docker`. Docker Engine 29.x elevou a API mínima suportada para 1.40+, rejeitando esse client — sintoma: `"Failed to retrieve information of the docker client and server host"` em loop, container fica `unhealthy`, nenhuma rota via label é descoberta (o file provider com Keycloak continua funcionando, mascarando parcialmente o problema). Não é resolvível via env `DOCKER_API_VERSION` (o client da v3.2 não respeita a env var). Corrigido subindo a imagem para **`traefik:v3.6`**, que implementa auto-negociação de versão da API Docker ([traefik/traefik#12253](https://github.com/traefik/traefik/issues/12253)). Se o host tiver Docker Engine < 29, v3.2 continua funcionando normalmente — o problema só se manifesta com engines novos.

## Consequências

**Positivo:**
- Roteamento dinâmico sem restart (hot-reload via file watcher)
- Dashboard web em `https://traefik.localhost/dashboard/` (restrito a IP interno)
- Path natural para Kubernetes IngressRoute
- Menos configuração vs. Nginx para casos complexos (múltiplos services, middlewares encadeados)

**Negativo/Trade-off:**
- Sintaxe de labels Docker pode ser verbosa
- Debugging inicial mais difícil (erros de label são silenciosos — verificar logs do Traefik)

## Alternativas descartadas

- **Nginx**: problemas com regex complexo, config estática, sem dashboard nativo
- **Caddy**: mais simples mas sem ecossistema de middleware comparável; menos adotado em ambientes Gov BR

## Referências

- [traefik/traefik.yaml](/gateway/traefik/traefik.yaml)
- [traefik/dynamic.yaml](/gateway/traefik/dynamic.yaml)
- [docker-compose.yaml](/gateway/docker-compose.yaml)
