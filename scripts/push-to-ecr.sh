###
# This scripts builds, tags and pushes the lambda image to AWS ECR
###

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 992382607343.dkr.ecr.us-east-1.amazonaws.com

echo "Building image..."
docker build -t bucha-bot .
echo "Done."

echo "Tagging image..."
docker tag bucha-bot:latest 992382607343.dkr.ecr.us-east-1.amazonaws.com/bucha-bot:latest
echo "Done."

echo "Pushing image to ECR..."
docker push 992382607343.dkr.ecr.us-east-1.amazonaws.com/bucha-bot:latest
echo "Done."