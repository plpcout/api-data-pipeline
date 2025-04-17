resource "google_service_account" "pipeline_service_account" {
  account_id   = var.service_account_name
  display_name = "Earthquake Pipeline Service Account"
  description  = "Service account for earthquake data pipeline operations"
}

resource "google_service_account_key" "pipeline_service_account_key" {
  service_account_id = google_service_account.pipeline_service_account.name
}

# Project - BigQuery permissions
resource "google_project_iam_member" "bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.pipeline_service_account.email}"
}

# Project - Storage permissions
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.pipeline_service_account.email}"
}