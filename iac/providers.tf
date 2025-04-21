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
    kestra = {
      source  = "kestra-io/kestra"
      version = "0.22.0"
    }
    tls = {
      source  = "hashicorp/tls"
      version = "~> 4.0"
    }
    local = {
      source  = "hashicorp/local"
      version = "~> 2.0"
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

provider "kestra" {
  # Configuration options
  url = "http://${google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip}:8080"
}