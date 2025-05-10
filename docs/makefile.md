# Makefile Guide

This document explains how to use the Makefile commands in this project. The Makefile provides a set of automated commands to help you manage the project's infrastructure and pipeline operations.

## Prerequisites

Before using the Makefile commands, ensure you have:

1. A `.env` file in the project root with required variables:

   ```bash
   GCP_PROJECT_ID=your-gcp-project-id
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
   ENV=dev
   ```

2. Google Cloud SDK installed and initialized
3. Terraform installed
4. Make utility installed

## Available Commands

### View Available Commands

```bash
make help
```

This will show all available commands with their descriptions.

### Infrastructure Management

1. **Authentication**

   ```bash
   make gcloud-sa-auth
   ```

   Authenticates with Google Cloud using your service account credentials.

2. **Enable Required APIs**

   ```bash
   make activate-apis
   ```

   Enables all necessary Google Cloud APIs for the project, including:
   - BigQuery
   - Cloud Build
   - Compute Engine
   - IAM
   - Cloud Storage
   - And more...

3. **Deploy Infrastructure**

   ```bash
   make up
   ```

   - Initializes Terraform
   - Creates/updates all cloud infrastructure
   - Uses variables from your .env file

4. **Destroy Infrastructure**

   ```bash
   make down
   ```

   Tears down all Terraform-managed infrastructure in your GCP project.

### Pipeline Operations

1. **Access Kestra UI**

   ```bash
   make app-ui
   ```

   Opens the Kestra orchestration UI in your default browser.

2. **Run Data Backfill**

   ```bash
   # Default: from 2024-01-01 to previous month
   make backfill

   # With custom dates
   make backfill start=2024-03-01 end=2024-03-31
   ```

   Triggers a backfill operation for historical earthquake data.

3. **Run DBT Transformations**

   ```bash
   # Using environment from .env file
   make dbt-run

   # Specify environment explicitly
   make dbt-run env=dev  # or env=stg or env=prod
   ```

   Executes DBT transformations on the ingested data.

4. **Run DBT with Full Refresh**

   ```bash
   # Using environment from .env file
   make fr-dbt-run

   # Specify environment explicitly
   make fr-dbt-run env=dev  # or env=stg or env=prod
   ```

    Runs DBT transformations with a full refresh, recreating the tables in BigQuery.
    - This command is particularly useful after significant changes to the data pipeline or when new data sources are integrated.

## Project Execution Order

1. Set up `.env` file
2. `make gcloud-sa-auth`
3. `make activate-apis`
4. `make up`
5. `make app-ui` (to verify deployment)
6. `make backfill` (to load historical data)
7. `make dbt-run` (to transform loaded data)

When you're done with the project, you can tear down all the infrastructure with:

```bash
make down
```

## Error Handling

- Make commands use color-coded output:
  - 🟢 Green: Success messages
  - 🟡 Yellow: Processing/warning messages
  - 🔴 Red: Error messages
- Most commands include error checking and will exit with helpful messages if something goes wrong
- Authentication and environment variable checks are built into relevant commands

## Environment Variables

The Makefile automatically loads these variables from your `.env` file:

- `GOOGLE_APPLICATION_CREDENTIALS`: Path to service account key
- `GCP_PROJECT_ID`: Your GCP project ID
- `ENV`: Environment (dev/stg/prod)

You can source the `.env` file manually if needed for other purposes:

```bash
set -o allexport
source .env
set +o allexport
```
