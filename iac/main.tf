terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "6.30.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "3.5.0"
    }

  }
}

provider "google" {
  # Configuration options
  project = var.project_id
  region  = var.region
}




