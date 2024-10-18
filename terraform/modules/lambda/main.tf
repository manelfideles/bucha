module "lambda_function" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "7.9.0"

  function_name = var.lambda_function_name
  description   = "The main scraper code"
  handler       = "main.handler"
  runtime       = "python3.12"

  create_package = false
  image_uri      = var.image_uri
  package_type   = "Image"

  attach_policy_json = true
  policy_json = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage",
          "ecr:BatchCheckLayerAvailability"
        ]
        Resource = var.repository_arn
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name = "buchabot"
  }

  environment_variables = {
    SLACK_INCOMING_WEBHOOK_URL = var.slack_incoming_webhook_url
    FACEBOOK_USERNAME          = var.facebook_username
    FACEBOOK_PASSWORD          = var.facebook_password
  }
}
