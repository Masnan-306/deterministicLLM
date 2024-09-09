docker build -f Dockerfile -t chat_service --platform=linux/amd64 .

az acr list --output table
az acr login --name {myregistry}
docker tag chat_service:latest {myregistry}.azurecr.io/chat_service:{v1}
docker push {myregistry.azurecr.io}/chat_service:{v1}

terraform init
terraform apply --auto-approve