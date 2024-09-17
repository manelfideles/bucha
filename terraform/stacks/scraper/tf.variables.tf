variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "facebook_username" {
  type = string
}

variable "facebook_password" {
  type      = string
  sensitive = true
}

variable "slack_incoming_webhook_url" {
  type = string
}
