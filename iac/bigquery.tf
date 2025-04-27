resource "google_bigquery_dataset" "earthquake_dataset" {
  dataset_id                 = "${var.env}_api_raw_${var.bigquery_dataset_id}"
  friendly_name              = "Earthquake Data"
  description                = "Dataset containing earthquake data and analytics"
  location                   = var.region
  delete_contents_on_destroy = true

  labels = {
    environment = var.env
  }
}

locals {
  datasets = [
    {
      dataset_id    = "${var.env}_dbt_raw"
      friendly_name = "Earthquake raw data"
      description   = "Dataset containing earthquake raw data"
    },
    {
      dataset_id    = "${var.env}_dbt_staging"
      friendly_name = "Earthquake staging data"
      description   = "Dataset containing staging data for processing"
    },
    {
      dataset_id    = "${var.env}_dbt_intermediate"
      friendly_name = "Earthquake Intermediate Data"
      description   = "Dataset containing intermediate processing data"
    },
    {
      dataset_id    = "${var.env}_dbt_mart"
      friendly_name = "Earthquake Mart Data"
      description   = "Dataset containing mart data for analytics"
    }
  ]
}

resource "google_bigquery_dataset" "datasets" {
  for_each                   = { for idx, ds in local.datasets : ds.dataset_id => ds }
  dataset_id                 = each.value.dataset_id
  friendly_name              = each.value.friendly_name
  description                = each.value.description
  location                   = var.region
  delete_contents_on_destroy = true
  labels = {
    environment = var.env
  }
}