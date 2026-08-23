output "order_service_url" {
  description = "URL of the order service"
  value       = "http://localhost:${var.order_port}"
}

output "payment_service_url" {
  description = "URL of the payment service"
  value       = "http://localhost:${var.payment_port}"
}

output "network_name" {
  description = "Name of the Docker network created by Terraform"
  value       = docker_network.app.name
}
