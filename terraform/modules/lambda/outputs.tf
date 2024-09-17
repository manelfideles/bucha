output "lambda_function_slack_webhook_url" {
  value = var.slack_incoming_webhook_url
}

output "lambda_function_arn" {
  value = module.lambda_function.lambda_function_arn
}

output "lambda_function_last_modified" {
  value = module.lambda_function.lambda_function_last_modified
}
