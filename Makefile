PROJECT_NAME = CustomerAnalysisService

.PHONY: help
help:
		@echo $(PROJECT_NAME)

.PHONY: up
up:
		docker compose -f docker-compose-local.yaml --profile dev --profile flower up -d

.PHONY: down
down:
		docker compose -f docker-compose-local.yaml --profile dev --profile flower down && docker network prune --force

.PHONY: worker
worker:
		poetry run celery -A cas_worker.worker.cas_worker worker -P solo

.PHONY: export-dep-all
export-dep-all:
		poetry export --without-hashes --with api --with worker --with dev -f requirements.txt -o ./requirements.txt

.PHONY: export-dep-api
export-dep-api:
		poetry export --without-hashes --with api -f requirements.txt -o ./deploy/requirements_api.txt

.PHONY: export-dep-worker
export-dep-worker:
		poetry export --without-hashes --with worker -f requirements.txt -o ./deploy/requirements_worker.txt

# Alembic
.PHONY: generate
generate:
		poetry run alembic revision --m="$(m)" --autogenerate

.PHONY: migrate
migrate:
		poetry run alembic upgrade head
