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
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    time = {
      source  = "hashicorp/time"
      version = "0.13.0"
    }
  }
}

provider "google" {
  # Configuration options
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

data "google_project" "default" {}
