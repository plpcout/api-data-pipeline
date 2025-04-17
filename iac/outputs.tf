output "gcs_bucket_name" {
  description = "The name of the GCS bucket created"
  value       = google_storage_bucket.earthquake_bucket.name
}

output "bigquery_dataset_id" {
  description = "The ID of the BigQuery dataset created"
  value       = google_bigquery_dataset.earthquake_dataset.dataset_id
}

output "service_account_email" {
  description = "The email of the service account created for the pipeline"
  value       = google_service_account.pipeline_service_account.email
}
