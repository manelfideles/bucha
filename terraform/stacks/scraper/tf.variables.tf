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

variable "lambda_function_name" {
  type    = string
  default = "bucha-bot"
}

variable "repository_name" {
  type    = string
  default = "bucha-bot"
}

variable "image_uri" {
  type = string
}

variable "schedule_expression" {
  type = string
}
