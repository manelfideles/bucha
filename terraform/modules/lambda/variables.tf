variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "slack_incoming_webhook_url" {
  type    = string
  default = "https://hooks.slack.com/services/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"
}

variable "facebook_username" {
  type = string
}

variable "facebook_password" {
  type      = string
  sensitive = true
}
