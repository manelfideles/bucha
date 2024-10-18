module "eventbridge" {
  source = "terraform-aws-modules/eventbridge/aws"

  create_bus = false

  rules = {
    lambda-scheduler = {
      description         = "Trigger Lambda function"
      schedule_expression = var.schedule_expression
    }
  }

  targets = {
    lambda-scheduler = [
      {
        name  = "trigger-scraper-lambda"
        arn   = var.lambda_function_arn
        input = jsonencode({ "detail-type" : "scheduled-event" })
      }
    ]
  }
}

resource "aws_lambda_permission" "allow_eventbridge" {
  statement_id  = "AllowEventBridgeInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_function_name
  principal     = "events.amazonaws.com"
  source_arn    = module.eventbridge.eventbridge_rule_arns["lambda-scheduler"]
}
