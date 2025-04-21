terraform {
  backend "gcs" {
    bucket = "terraform-state-earthquake-pipeline"
    prefix = "terraform/state"
  }
}