###
# [Legacy] This script deploys the lambda to localstack.
###

echo "Zipping lambda function..."
rm lambda.zip
rm lambda.json
cd src
zip -rq1 ../lambda.zip .
cd ..
echo "Done."

echo "Applying infrastructure changes..."
cd terraform/stacks/scraper
terraform apply -auto-approve -var-file=workspaces/dev.tfvars
echo "Done."

echo "Deploying lambda function..."
cd ../../../
aws --profile localstack lambda invoke --function-name buchabot lambda.json
echo "Done."

