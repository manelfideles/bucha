variable "repository_name" {
  type        = string
  description = "The name of the ECR repository"
  default     = "lambda-container-image"
}

variable "keep_last_N" {
  type        = number
  description = "The number of past image builds to keep in the repo."
  default     = 5
}
