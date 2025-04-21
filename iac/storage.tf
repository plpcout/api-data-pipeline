# https://registry.terraform.io/providers/hashicorp/random/latest/docs/resources/uuid
resource "random_uuid" "bucket_random_id" {
  keepers = {
    bucket_prefix = var.environment
  }
}

resource "google_storage_bucket" "earthquake_bucket" {
  name          = "${var.environment}-${var.gcs_bucket_name}-${random_uuid.bucket_random_id.result}"
  location      = var.region
  force_destroy = true

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 30 # days
    }
    action {
      type = "Delete"
    }
  }
}
