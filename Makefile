# Include and export environment variables from .env to make environment
ifneq (,$(wildcard .env))
    include .env
    export
endif


# COLORS
RESET	:= $(shell tput -Txterm sgr0)
RED		:= $(shell tput -Txterm setaf 1)
GREEN	:= $(shell tput -Txterm setaf 2)
YELLOW 	:= $(shell tput -Txterm setaf 3)
BLUE	:= $(shell tput -Txterm setaf 4)
PURPLE	:= $(shell tput -Txterm setaf 5)

TARGET_MAX_CHAR_NUM=20

## Show this help message
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make ${GREEN}<target> ${BLUE}<args>${RESET}' 
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

.PHONY: gcloud-sa-auth
## Authenticate with Google Cloud using service account credentials
gcloud-sa-auth:
	@if ! gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}; then \
		echo "${RED}Failed to authenticate with Google Cloud${RESET}"; \
		exit 1; \
	fi
	@if ! gcloud config set project ${GCP_PROJECT_ID}; then \
		echo "${RED}Failed to set Google Cloud project${RESET}"; \
		exit 1; \
	fi
	@echo "${GREEN}Authenticated with Google Cloud using service account and set project to: ${RESET}${GCP_PROJECT_ID}"


.PHONY: activate-apis
## Enable required Google Cloud APIs for the project
activate-apis:
	@echo "${YELLOW}Enabling required APIs...${RESET}"
	@if ! gcloud services enable \
		bigquery.googleapis.com \
		bigquerydatatransfer.googleapis.com \
		cloudbuild.googleapis.com \
		container.googleapis.com \
		compute.googleapis.com \
		iam.googleapis.com \
		logging.googleapis.com \
		monitoring.googleapis.com \
		pubsub.googleapis.com \
		storage.googleapis.com \
		cloudresourcemanager.googleapis.com; then \
		echo "${RED}Error: Failed to enable one or more APIs${RESET}"; \
		exit 1; \
	fi
	@echo "${GREEN}Required APIs have been successfully activated for project: ${RESET}${GCP_PROJECT_ID}${RESET}"

.PHONY: up
## Initialize Terraform and provision cloud infrastructure setup
up:
	@terraform -chdir=iac init && \
	terraform -chdir=iac apply --auto-approve \
		--var project_id=${GCP_PROJECT_ID} \
		--var env=${ENV}

.PHONY: app-ui
## Open Kestra UI in default browser
app-ui:
	@xdg-open "$$(terraform -chdir=iac output -raw kestra_ui_url)" > /dev/null 2>&1 || \
	(echo "${RED}Failed to open Kestra UI. Please visit the URL manually: ${YELLOW}$(terraform -chdir=iac output -raw kestra_ui_url)${RESET}" && exit 1)


.PHONY: backfill
## Trigger backfill | Default: From 2024-01-01 to the previous month | Usage: make backfill [start=YYYY-MM-DD] [end=YYYY-MM-DD]
backfill:
	$(eval start ?= 2024-01-01)
	$(eval end ?= $(shell date -d "$(shell date +%Y-%m-01) -1 day" +%Y-%m-%d))
	$(eval API_URL := $(shell terraform -chdir=iac output -raw kestra_ui_url))
	@curl -X PUT "$(API_URL)/api/v1/triggers" \
		-H 'Content-Type: application/json' \
		-d "{\
			\"backfill\": {\
				\"start\": \"$(start)T00:00:00.000Z\",\
				\"end\": \"$(end)T00:00:00.000Z\",\
				\"inputs\": null,\
				\"labels\": [{\
					\"key\": \"backfill\",\
					\"value\": \"true\"\
				},\
				{\
					\"key\": \"call\",\
					\"value\": \"api\"\
				}]\
			},\
			\"flowId\": \"api-to-bq-gcs-stg\",\
			\"namespace\": \"eq-proj\",\
			\"triggerId\": \"trigger_run\"\
		}"
	@echo "\n\n${GREEN}Backfill triggered${RESET}"
	@echo "\n${YELLOW}Check Kestra UI for the backfill execution status.${RESET}"
	@echo "$(shell terraform -chdir=iac output -raw kestra_ui_url)/ui/flows/edit/eq-proj/api-to-bq-gcs-stg/executions"


.PHONY: dbt-run
## Run dbt transformations | Default: env=dev | Usage: make dbt-run [env=dev|stg|prod]
dbt-run:
	@if [ -z "${ENV}" ]; then \
		echo "${RED}Error: ENV variable is not set.${RESET}"; \
		exit 1; \
	fi
	@$(eval API_URL := $(shell terraform -chdir=iac output -raw kestra_ui_url))
	@curl -v -X POST \
		-H 'Content-Type: multipart/form-data' \
		-F 'dbt_env=${ENV}' \
		'$(API_URL)/api/v1/executions/eq-proj/dbt?labels=call:api&labels=run:dbt'
	
	@echo "\n\n${GREEN}DBT run triggered${RESET}" 
	@echo "\n${YELLOW}Check Kestra UI for the execution status.${RESET}"
	@echo "$(shell terraform -chdir=iac output -raw kestra_ui_url)/ui/flows/edit/eq-proj/dbt/executions"


###### --full-refresh
.PHONY: fr-dbt-run
## Run dbt transformations with full refresh | Default: env=dev | Usage: make fr-dbt-run [env=dev|stg|prod]
fr-dbt-run:
	@if [ -z "${ENV}" ]; then \
		echo "${RED}Error: ENV variable is not set.${RESET}"; \
		exit 1; \
	fi
	@$(eval API_URL := $(shell terraform -chdir=iac output -raw kestra_ui_url))
	@curl -v -X POST \
		-H 'Content-Type: multipart/form-data' \
		-F 'dbt_env=${ENV}' \
		-F 'full_refresh=true' \
		'$(API_URL)/api/v1/executions/eq-proj/dbt?labels=call:api&labels=run:full-refresh'
	
	@echo "\n\n${GREEN}DBT full refresh triggered${RESET}" 
	@echo "\n${YELLOW}Check Kestra UI for the execution status.${RESET}"
	@echo "$(shell terraform -chdir=iac output -raw kestra_ui_url)/ui/flows/edit/eq-proj/dbt/executions"

.PHONY: down
## Destroy Terraform-managed cloud infrastructure
down:

	@terraform -chdir=iac destroy --auto-approve \
		--var project_id=${GCP_PROJECT_ID} \
		--var env=${ENV}

