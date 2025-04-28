# Generate a new SSH key pair
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
}

# Store the private key locally for use with provisioners
resource "local_file" "private_key" {
  content         = tls_private_key.ssh_key.private_key_pem
  filename        = "${path.module}/.ssh/generated_ssh_key"
  file_permission = "0600"
}

# Optional: Store the public key locally for reference
resource "local_file" "public_key" {
  content         = tls_private_key.ssh_key.public_key_openssh
  filename        = "${path.module}/.ssh/generated_ssh_key.pub"
  file_permission = "0644"
}