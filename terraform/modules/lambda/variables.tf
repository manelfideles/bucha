variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "slack_incoming_webhook_url" {
  type      = string
  sensitive = true
}

variable "facebook_username" {
  type = string
}

variable "facebook_password" {
  type      = string
  sensitive = true
}

variable "lambda_function_name" {
  type = string
}

variable "image_uri" {
  type = string
}

variable "repository_arn" {
  type = string
}
