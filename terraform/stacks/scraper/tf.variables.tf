variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "lambda_function_name" {
  type    = string
  default = "bucha-bot-lambda"
}

variable "repository_name" {
  type    = string
  default = "bucha-bot-repository"
}

variable "image_uri" {
  type = string
}

variable "schedule_expression" {
  type    = string
  default = "cron(45 11 ? * MON-FRI *)"
}
