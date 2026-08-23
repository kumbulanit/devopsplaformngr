# Infrastructure as Code lab: provision the sample microservices on Docker.
# This uses the local Docker provider so no cloud account is required.

resource "docker_network" "app" {
  name = "tf-${var.environment}-app-network"
}

resource "docker_container" "payment_service" {
  name  = "tf-${var.environment}-payment-service"
  image = var.payment_image

  env = [
    "APP_ENV=${var.environment}",
    "BUILD_ID=terraform-${var.environment}",
  ]

  ports {
    internal = 8000
    external = var.payment_port
  }

  networks_advanced {
    name = docker_network.app.name
  }

  healthcheck {
    test     = ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
    interval = "10s"
    timeout  = "3s"
    retries  = 3
  }
}

resource "docker_container" "order_service" {
  name  = "tf-${var.environment}-order-service"
  image = var.order_image

  env = [
    "APP_ENV=${var.environment}",
    "BUILD_ID=terraform-${var.environment}",
    "PAYMENT_SERVICE_URL=http://${docker_container.payment_service.name}:8000",
  ]

  ports {
    internal = 8000
    external = var.order_port
  }

  networks_advanced {
    name = docker_network.app.name
  }

  depends_on = [docker_container.payment_service]

  healthcheck {
    test     = ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
    interval = "10s"
    timeout  = "3s"
    retries  = 3
  }
}
