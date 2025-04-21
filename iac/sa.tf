# Service account for the Kestra VM
resource "google_service_account" "kestra_service_account" {
  account_id   = "kestra-sa"
  display_name = "Kestra Service Account"
  description  = "Service account for Kestra orchestration VM"
}

# Grant roles to the Kestra service account
resource "google_project_iam_member" "storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.kestra_service_account.email}"
}

# Grant roles to the Kestra service account
resource "google_project_iam_member" "bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.kestra_service_account.email}"
}

# Allow the Kestra VM to use the service account
resource "google_service_account_iam_binding" "kestra_sa_user" {
  service_account_id = google_service_account.kestra_service_account.name
  role               = "roles/iam.serviceAccountUser"
  members = [
    "serviceAccount:${google_service_account.kestra_service_account.email}",
  ]
}

resource "google_service_account_key" "kestra_service_account_key" {
  service_account_id = google_service_account.kestra_service_account.name
}