#!/bin/bash


az acr list --output table
export TF_VAR_image_repository_name="deterministicchatservicee"
export TF_VAR_image_tag="v1.0"
export KUBECONFIG="/Users/zhinanwang/.kube_config.yaml"

az acr login --name $TF_VAR_image_repository_name
az acr credential show --name $TF_VAR_image_repository_name

# Fetch ACR credentials
echo "Fetching ACR credentials..."
ACR_CREDENTIALS=$(az acr credential show --name $TF_VAR_image_repository_name --output json)

# Extract username, password, and use your Azure account email
export ACR_USERNAME=$(echo $ACR_CREDENTIALS | jq -r '.username')
export ACR_PASSWORD=$(echo $ACR_CREDENTIALS | jq -r '.passwords[0].value')
export ACR_EMAIL="zhinanw@andrew.cmu.edu"

# Export environment variables for Terraform
echo "Exporting environment variables..."
export TF_VAR_acr_username="$ACR_USERNAME"
export TF_VAR_acr_password="$ACR_PASSWORD"
export TF_VAR_acr_email="$ACR_EMAIL"

# Confirm variables are set
echo "TF_VAR_acr_username set to $TF_VAR_acr_username"
echo "TF_VAR_acr_password set to [HIDDEN]"
echo "TF_VAR_acr_email set to $TF_VAR_acr_email"

echo "Environment variables are set successfully."

# docker build -f Dockerfile -t chat_service --platform=linux/amd64 .
# docker tag chat_service:latest $TF_VAR_image_repository_name.azurecr.io/chat_service:$TF_VAR_image_tag
# docker push $TF_VAR_image_repository_name.azurecr.io/chat_service:$TF_VAR_image_tag

terraform init
terraform apply --auto-approve