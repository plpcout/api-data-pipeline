resource "google_bigquery_dataset" "earthquake_dataset" {
  dataset_id                 = var.bigquery_dataset_id
  friendly_name              = "Earthquake Data"
  description                = "Dataset containing earthquake data and analytics"
  location                   = var.region
  delete_contents_on_destroy = true

  labels = {
    environment = var.environment
  }
}