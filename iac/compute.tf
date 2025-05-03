# Create a static IP address
resource "google_compute_address" "static_ip" {
  name = "${var.kestra_vm_name}-static-ip"
}
# Create a GCP VM instance
resource "google_compute_instance" "kestra_vm" {
  name         = var.kestra_vm_name
  machine_type = var.kestra_machine_type


  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts"
      size  = 30
    }
  }

  network_interface {
    network = "default"
    access_config {
      nat_ip = google_compute_address.static_ip.address
    }
  }

  metadata = {
    ssh-keys       = "${var.ssh_user}:${tls_private_key.ssh_key.public_key_openssh}"
    user-data      = file("${path.module}/startup.sh")
    startup-script = <<-EOF
      cd /opt/kestra
      sudo docker compose up -d
    EOF
  }
  service_account {
    email  = google_service_account.kestra_service_account.email
    scopes = ["cloud-platform"]
  }

  resource_policies = [google_compute_resource_policy.monthly_boot.id]
  
  # Allow HTTP/HTTPS traffic
  tags                      = ["http-server", "https-server"]
  allow_stopping_for_update = true
}

# Firewall rule for Kestra UI
resource "google_compute_firewall" "kestra-ui" {
  name    = "allow-kestra-ui"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["8080"] # Default Kestra UI port
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["http-server", "https-server"]
}

resource "google_compute_resource_policy" "monthly_boot" {
  name        = "resource-policy-monthly-boot"
  region      = var.region
  description = "Monthly boot policy"
  instance_schedule_policy {
    time_zone = "UTC"

    # Schedule for the VM to start at 3:00 AM UTC on the first day of every month
    vm_start_schedule {
      schedule = "0 3 1 * *"
    }
    
    # Schedule for the VM to stop at 4:00 AM UTC on the first day of every month
    vm_stop_schedule {
      schedule = "0 4 1 * *"
    }
  }
}

