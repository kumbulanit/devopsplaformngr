variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "dev"
}

variable "order_image" {
  description = "Docker image for the order service"
  type        = string
  default     = "order-service:lab02"
}

variable "payment_image" {
  description = "Docker image for the payment service"
  type        = string
  default     = "payment-service:lab02"
}

variable "order_port" {
  description = "Host port mapped to the order service"
  type        = number
  default     = 8090
}

variable "payment_port" {
  description = "Host port mapped to the payment service"
  type        = number
  default     = 8091
}
