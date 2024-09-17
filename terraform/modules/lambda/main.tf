module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.9.0"

  function_name = "buchabot"
  description   = "The main scraper code"
  handler       = "bucha.main.handler"
  runtime       = "python3.12"

  create_package         = false
  local_existing_package = "../../../lambda.zip"

  tags = {
    Name = "buchabot"
  }

  environment_variables = {
    SLACK_INCOMING_WEBHOOK_URL = var.slack_incoming_webhook_url
    FACEBOOK_USERNAME          = var.facebook_username
    FACEBOOK_PASSWORD          = var.facebook_password
  }
}
