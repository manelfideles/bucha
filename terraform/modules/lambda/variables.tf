variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "slack_incoming_webhook_url" {
  type = string
}

variable "facebook_username" {
  type = string
}

variable "facebook_password" {
  type      = string
  sensitive = true
}
