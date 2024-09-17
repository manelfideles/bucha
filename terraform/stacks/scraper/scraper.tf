# lambda module
module "lambda_function" {
  source                     = "../../modules/lambda"
  facebook_username          = var.facebook_username
  facebook_password          = var.facebook_password
  slack_incoming_webhook_url = var.slack_incoming_webhook_url
}


# ecr module
# eventbridge module
