locals {
  google_vars = <<-EOT
    #!/bin/bash
    # Remove old GOOGLE_APPLICATION_CREDENTIALS line if it exists
    sed -i '/^GOOGLE_APPLICATION_CREDENTIALS=/d' /opt/kestra/.env

    echo ${google_service_account_key.kestra_service_account_key.private_key} | base64 -d > /opt/kestra/.gcp/credentials.json
    
    # Append new GOOGLE_APPLICATION_CREDENTIALS and a blank line
    {
        echo "GOOGLE_APPLICATION_CREDENTIALS=\"/opt/kestra/.gcp/credentials.json\""
        cat /opt/kestra/.env
    } > /opt/kestra/.env.tmp && mv /opt/kestra/.env.tmp /opt/kestra/.env
    EOT

  dlt_vars = <<-EOT
    #!/bin/bash
    # Remove old DESTINATION__FILESYSTEM__BUCKET_URL line if it exists
    sed -i '/^DESTINATION__FILESYSTEM__BUCKET_URL=/d' /opt/kestra/.env

    # Append new DESTINATION__FILESYSTEM__BUCKET_URL at the top of the file
    {
        echo "DESTINATION__FILESYSTEM__BUCKET_URL=\"${google_storage_bucket.earthquake_bucket.url}\""
        cat /opt/kestra/.env
    } > /opt/kestra/.env.tmp && mv /opt/kestra/.env.tmp /opt/kestra/.env

    # Remove old DESTINATION__BIGQUERY__DATASET_NAME line if it exists
    sed -i '/^DESTINATION__BIGQUERY__DATASET_NAME=/d' /opt/kestra/.env
    echo DESTINATION__BIGQUERY__DATASET_NAME "${google_bigquery_dataset.earthquake_dataset.dataset_id}"

    # Append new DESTINATION__BIGQUERY__DATASET_NAME at the top of the file
    {
        echo "DESTINATION__BIGQUERY__DATASET_NAME=\"${google_bigquery_dataset.earthquake_dataset.dataset_id}\""
        cat /opt/kestra/.env
    } > /opt/kestra/.env.tmp && mv /opt/kestra/.env.tmp /opt/kestra/.env
    EOT
}
# Null resource to provisioners for file transfer and remote execution
resource "null_resource" "deploy_kestra" {
  # Trigger a redeploy when any of these changes
  triggers = {
    instance_id = google_compute_instance.kestra_vm.id
  }

  # Wait for VM to be ready and SSH to be available
  provisioner "remote-exec" {
    inline = [
      "echo 'SSH connection established'",
      "sudo mkdir -p /opt/kestra/files /opt/kestra/flows /opt/kestra/.gcp",
      "sudo chown -R ${var.ssh_user}:${var.ssh_user} /opt/kestra/",
    ]

    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = tls_private_key.ssh_key.private_key_pem
      host        = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
      # Add a timeout to ensure we wait for the VM to be fully initialized
    }
  }

  # Copy Kestra files needed.
  provisioner "file" {
    source      = var.kestra_dir_path
    destination = "/opt/kestra/"

    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = tls_private_key.ssh_key.private_key_pem
      host        = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
    }
  }

  provisioner "file" {
    source      = "../.env"
    destination = "/opt/kestra/.env"

    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = tls_private_key.ssh_key.private_key_pem
      host        = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
    }
  }

  provisioner "remote-exec" {
    inline = [
      local.dlt_vars,
      local.google_vars,
      #   local.kestra_vars
    ]
  }

  connection {
    type        = "ssh"
    user        = var.ssh_user
    private_key = tls_private_key.ssh_key.private_key_pem
    host        = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
    timeout     = "5m"
  }
  depends_on = [google_compute_instance.kestra_vm]
}

resource "time_sleep" "resource_waiting" {
  depends_on      = [null_resource.deploy_kestra]
  create_duration = "60s"
}

# Null resource to provisioners for file transfer and remote execution
resource "null_resource" "run_kestra" {
  # Trigger a redeploy when any of these changes
  #   triggers = {
  #     instance_id = google_compute_instance.kestra_vm.id
  #   }

  # Start Docker Compose
  provisioner "remote-exec" {
    inline = [
      "cd /opt/kestra",
      "sudo docker compose up -d"
    ]

    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = tls_private_key.ssh_key.private_key_pem
      host        = google_compute_instance.kestra_vm.network_interface[0].access_config[0].nat_ip
      timeout     = "5m"
    }
  }
  depends_on = [null_resource.deploy_kestra, time_sleep.resource_waiting]
}
