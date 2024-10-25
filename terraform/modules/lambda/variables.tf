variable "aws_region" {
  type    = string
  default = "us-east-1"
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
