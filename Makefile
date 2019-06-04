# ==============================================================================
# VARIABLES

# -- Docker
# Get the current user ID to use for docker run and docker exec commands
DOCKER_UID           = $(shell id -u)
DOCKER_GID           = $(shell id -g)
DOCKER_USER          = $(DOCKER_UID):$(DOCKER_GID)
COMPOSE              = DOCKER_USER=$(DOCKER_USER) docker-compose
COMPOSE_RUN          = $(COMPOSE) run --rm
COMPOSE_RUN_APP      = $(COMPOSE_RUN) app
COMPOSE_EXEC         = $(COMPOSE) exec
COMPOSE_EXEC_APP     = $(COMPOSE_EXEC) app

# ==============================================================================
# RULES

default: help

# -- Docker/compose
build: ## build the app container
	@$(COMPOSE) build app
.PHONY: build

dev: run logs ## start development (run development server with logs)
.PHONY: dev

logs: ## get application logs
	@$(COMPOSE) logs -f app
.PHONY: logs

run: ## run development web server
	@$(COMPOSE) up -d app
.PHONY: run

status: ## get stack status
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop the development server
	@$(COMPOSE) stop
.PHONY: stop

# -- Back-end

test: ## run tests
	@$(COMPOSE_RUN_APP) pytest
.PHONY: test

# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
