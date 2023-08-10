PROJECT_NAME = CustomerAnalysisService

.PHONY: help
help:
		@echo $(PROJECT_NAME)

.PHONY: up
up:
		docker compose -f docker-compose-local.yaml --profile dev --profile flower up -d

.PHONY: down
down:
		docker compose -f docker-compose-local.yaml down && docker network prune --force

# Alembic
.PHONY: generate
generate:
	poetry run alembic revision --m="$(m)" --autogenerate

.PHONY: migrate
migrate:
	poetry run alembic upgrade head
