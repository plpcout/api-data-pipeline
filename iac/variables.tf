variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default GCP region for resource creation"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The default GCP zone for resource creation"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment (dev/stg/prod)"
  type        = string
  default     = "dev"
}

variable "gcs_bucket_name" {
  description = "Name of the GCS bucket for storing earthquake data"
  type        = string
}

variable "bigquery_dataset_id" {
  description = "ID of the BigQuery dataset for earthquake data"
  type        = string
  default     = "earthquake_data"
}

variable "service_account_name" {
  description = "Name of the service account for the pipeline"
  type        = string
  default     = "earthquake-pipeline-sa"
}