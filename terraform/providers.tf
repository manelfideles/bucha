provider "aws" {
  region  = var.aws_region
  profile = "default"
  # skip_credentials_validation = true
  # skip_requesting_account_id  = true
  # skip_metadata_api_check     = true

  # endpoints {
  #   eventbridge    = "http://localhost:4566"
  #   cloudwatchlogs = "http://localhost:4566"
  #   dynamodb       = "http://localhost:4566"
  #   ecr            = "http://localhost:4566"
  #   lambda         = "http://localhost:4566"
  #   s3             = "http://s3.localhost.localstack.cloud:4566"
  #   sts            = "http://localhost:4566"
  #   iam            = "http://localhost:4566"
  # }
}
