variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The default GCP region for resource creation"
  type        = string
  default     = "US"
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
  default     = "earthquake-data-bucket"
}

variable "bigquery_dataset_id" {
  description = "ID of the BigQuery dataset for earthquake data"
  type        = string
  default     = "earthquake_data"
}

# Kestra Compute Engine variables
variable "kestra_vm_name" {
  description = "Name of the Compute Engine VM for Kestra"
  type        = string
  default     = "kestra-orchestrator"
}

variable "kestra_machine_type" {
  description = "Machine type for the Kestra VM"
  type        = string
  default     = "e2-standard-4"
}

variable "kestra_vm_tags" {
  description = "Network tags for the Kestra VM"
  type        = list(string)
  default     = ["https-server"]
}

variable "kestra_ui_port" {
  description = "Port on which Kestra UI will be accessible"
  type        = number
  default     = 8080
}

variable "kestra_boot_disk_size" {
  description = "Boot disk size for Kestra VM in GB"
  type        = number
  default     = 30
}

variable "ssh_user" {
  description = "SSH username"
  type        = string
  default     = "ubuntu"
}

variable "kestra_dir_path" {
  description = "Path to directory containing Kestra files"
  type        = string
  default     = "../src/kestra/"
}
