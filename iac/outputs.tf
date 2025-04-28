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
  #   value       = google_service_account.pipeline_service_account.email
  value = google_service_account.kestra_service_account.email
}

# Output the Kestra VM external IP
output "kestra_vm_external_ip" {
  value       = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
  description = "The external IP address of the Kestra VM"
}

# Output the Kestra UI URL
output "kestra_ui_url" {
  value       = "http://${google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip}:${var.kestra_ui_port}"
  description = "URL to access the Kestra UI"
}

output "kestra_service_account_key" {
  description = "The private key of the service account created for the pipeline"
  value       = google_service_account_key.kestra_service_account_key.private_key
  sensitive   = true
}