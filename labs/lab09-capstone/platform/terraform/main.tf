# Reusable Terraform module for the course sample application.
# A stream-aligned team consumes this module and only supplies environment-specific variables.

terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0"
    }
  }
}

variable "environment" {
  type = string
}

variable "order_image" {
  type = string
}

variable "payment_image" {
  type = string
}

variable "order_port" {
  type    = number
  default = 8090
}

variable "payment_port" {
  type    = number
  default = 8091
}

resource "docker_network" "app" {
  name = "platform-${var.environment}-network"
}

resource "docker_container" "payment" {
  name  = "platform-${var.environment}-payment"
  image = var.payment_image

  env = [
    "APP_ENV=${var.environment}",
    "BUILD_ID=platform-${var.environment}",
  ]

  ports {
    internal = 8000
    external = var.payment_port
  }

  networks_advanced {
    name = docker_network.app.name
  }
}

resource "docker_container" "order" {
  name  = "platform-${var.environment}-order"
  image = var.order_image

  env = [
    "APP_ENV=${var.environment}",
    "BUILD_ID=platform-${var.environment}",
    "PAYMENT_SERVICE_URL=http://${docker_container.payment.name}:8000",
  ]

  ports {
    internal = 8000
    external = var.order_port
  }

  networks_advanced {
    name = docker_network.app.name
  }

  depends_on = [docker_container.payment]
}

output "order_url" {
  value = "http://localhost:${var.order_port}"
}

output "payment_url" {
  value = "http://localhost:${var.payment_port}"
}
