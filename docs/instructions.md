# Project Setup & Replication - Step-by-Step

Follow these steps to replicate the project in a fresh environment.

## 1. Prerequisites

- Google Cloud account with billing enabled
- GCP Project (create a new one or use an existing one)
- Google Cloud SDK (gcloud) Installed
- Terraform Installed

## 2. Clone the repository

```bash
git clone https://github.com/plpcout/api-data-pipeline
cd api-data-pipeline
```

## 3. Configure environment variables

Create a `.env` in the project root:

```bash
cp .env.template .env
```

Edit `.env` to include your `GCP_PROJECT_ID` and `GOOGLE_APPLICATION_CREDENTIALS` .json key file path.:

```bash
GCP_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=/full/path/to/service-account.json
ENV=dev
```

## 4. GCP authentication & API enablement

Use the `make` commands to authenticate and enable APIs.
Additional info on make commands can be found in the [Makefile Guide](makefile.md).

```bash
make gcloud-sa-auth
```

```bash
make activate-apis
```

## 5. Provision infrastructure with Terraform

```bash
make up
```

> [!WARNING]
> This command will provision all cloud resources and may take a bit of time to complete (around 5 minutes).

## 6. Launch Kestra UI

This command opens the Kestra UI in your default browser.

```bash
make app-ui
```

## 7. Backfill data

- For default backfill run (starting from 2024-01-01)

    ```bash
    make backfill
    ```

- For custom backfill run (specify start and end dates)

    ```bash
    make backfill start=YYYY-MM-DD end=YYYY-MM-DD
    ```

Visit the execution URL provided in your terminal to monitor the backfill process.

## 8. Trigger DBT Transformations

- For default DBT run (using environment from `.env`)

    ```bash
    make dbt-run
    ```

## 9. Tear down

To destroy all Terraform-managed infrastructure, run:

```bash
make down
```

> [!WARNING]
> This command will delete all resources created by Terraform. Ensure you have backups of any important data you might want to preserve before proceeding.
