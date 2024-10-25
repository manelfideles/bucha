###
# This scripts builds, tags and pushes the lambda image to AWS ECR
###

REPOSITORY_URL="992382607343.dkr.ecr.us-east-1.amazonaws.com/bucha-bot-repository"

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $REPOSITORY_URL

echo "Building image..."
docker build -t bucha-bot:latest .
echo "Done."

echo "Tagging image..."
docker tag bucha-bot:latest $REPOSITORY_URL:latest
echo "Done."

echo "Pushing image to ECR..."
docker push $REPOSITORY_URL:latest
echo "Done."