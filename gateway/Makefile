.PHONY: up down restart logs status ps \
        create-squad-key list-keys revoke-key \
        gen-env check-env

COMPOSE = docker compose
GATEWAY_URL = https://localhost/key
ADMIN_URL   = https://localhost
MASTER_KEY ?= $(shell grep LITELLM_MASTER_KEY .env 2>/dev/null | cut -d= -f2)

# ── Stack ─────────────────────────────────────────────────────────────────────

up: check-env                    ## Subir todos os serviços
	$(COMPOSE) up -d --remove-orphans
	@echo ""
	@echo "Gateway:   https://localhost/v1"
	@echo "Grafana:   https://localhost/grafana  ($(shell grep GRAFANA_USER .env | cut -d= -f2))"
	@echo "Traefik:   https://traefik.localhost/dashboard/"
	@echo ""
	@$(MAKE) status

down:                            ## Parar todos os serviços
	$(COMPOSE) down

restart:                         ## Reiniciar sem recriar volumes
	$(COMPOSE) restart

logs:                            ## Seguir logs do gateway
	$(COMPOSE) logs -f litellm

ps:                              ## Status dos containers
	$(COMPOSE) ps

status:                          ## Health check do gateway
	@curl -sfk https://localhost/health 2>/dev/null || echo "gateway offline"

# ── Virtual Keys (squads) ─────────────────────────────────────────────────────

create-squad-key:                ## Criar virtual key para uma squad
	@test -n "$(SQUAD)" || (echo "Uso: make create-squad-key SQUAD=squad-dados [BUDGET=100]" && exit 1)
	@curl -sk -X POST $(ADMIN_URL)/key/generate \
		-H "Authorization: Bearer $(MASTER_KEY)" \
		-H "Content-Type: application/json" \
		-d '{"team_id":"$(SQUAD)","key_alias":"$(SQUAD)","max_budget":$(or $(BUDGET),50),"metadata":{"squad":"$(SQUAD)"}}' \
		| python3 -m json.tool

list-keys:                       ## Listar todas as virtual keys
	@curl -sk $(ADMIN_URL)/key/list \
		-H "Authorization: Bearer $(MASTER_KEY)" | python3 -m json.tool

revoke-key:                      ## Revogar uma virtual key
	@test -n "$(KEY)" || (echo "Uso: make revoke-key KEY=sk-..." && exit 1)
	@curl -sk -X DELETE $(ADMIN_URL)/key/delete \
		-H "Authorization: Bearer $(MASTER_KEY)" \
		-H "Content-Type: application/json" \
		-d '{"keys":["$(KEY)"]}' | python3 -m json.tool

# ── Setup ─────────────────────────────────────────────────────────────────────

gen-env:                         ## Gerar .env com senhas aleatórias
	@test ! -f .env || (echo ".env já existe — apague antes de regenerar" && exit 1)
	@cp .env.example .env
	@sed -i '' "s|LITELLM_MASTER_KEY=.*|LITELLM_MASTER_KEY=sk-litellm-$(shell openssl rand -hex 32)|" .env
	@sed -i '' "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(shell openssl rand -hex 16)|" .env
	@sed -i '' "s|GRAFANA_PASSWORD=.*|GRAFANA_PASSWORD=$(shell openssl rand -hex 12)|" .env
	@sed -i '' "s|KEYCLOAK_ADMIN_PASSWORD=.*|KEYCLOAK_ADMIN_PASSWORD=$(shell openssl rand -hex 16)|" .env
	@sed -i '' "s|KEYCLOAK_DB_PASSWORD=.*|KEYCLOAK_DB_PASSWORD=$(shell openssl rand -hex 16)|" .env
	@echo ".env gerado. Preencha as API keys dos provedores antes de rodar 'make up'."

check-env:
	@test -f .env || (echo "Erro: .env não encontrado. Execute 'make gen-env' e preencha as API keys." && exit 1)

help:                            ## Mostrar esta ajuda
	@grep -E '^[a-zA-Z_-]+:.*?##' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
