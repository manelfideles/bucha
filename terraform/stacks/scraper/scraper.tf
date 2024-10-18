# ecr module
module "ecr" {
  source          = "../../modules/ecr"
  repository_name = var.repository_name
  keep_last_N     = 5
}

# lambda module
module "lambda" {
  source                     = "../../modules/lambda"
  lambda_function_name       = var.lambda_function_name
  facebook_username          = var.facebook_username
  facebook_password          = var.facebook_password
  slack_incoming_webhook_url = var.slack_incoming_webhook_url
  image_uri                  = var.image_uri
  repository_arn             = module.ecr.repository_arn
}

# eventbridge module
module "eventbridge" {
  source               = "../../modules/eventbridge"
  lambda_function_arn  = module.lambda.lambda_function_arn
  lambda_function_name = module.lambda.lambda_function_name
  schedule_expression  = var.schedule_expression
}
