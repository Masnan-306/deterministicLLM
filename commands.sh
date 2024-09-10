#!/bin/bash

# Function to check the exit status of the previous command
check_exit_status() {
  if [ $? -ne 0 ]; then
    echo "Error occurred in the previous command. Exiting pipeline."
    exit 1
  fi
}


az acr list --output table
###################################################
# TODO: Replace the variables for your own trial  #
###################################################
export TF_VAR_image_repository_name="deterministicChatServicee"
export TF_VAR_image_tag="v2.0"
export TF_VAR_location="eastus"
export TF_VAR_kube_config_path="/Users/zhinanwang/.kube/config.yaml"
export KUBECONFIG=$TF_VAR_kube_config_path
check_exit_status

az acr login --name $TF_VAR_image_repository_name
az acr credential show --name $TF_VAR_image_repository_name
check_exit_status

# Fetch ACR credentials
echo "Fetching ACR credentials..."
ACR_CREDENTIALS=$(az acr credential show --name $TF_VAR_image_repository_name --output json)
# Extract username, password, and use your Azure account email
export ACR_USERNAME=$(echo $ACR_CREDENTIALS | jq -r '.username')
export ACR_PASSWORD=$(echo $ACR_CREDENTIALS | jq -r '.passwords[0].value')
export ACR_EMAIL="zhinanw@andrew.cmu.edu"
check_exit_status

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

docker login $TF_VAR_image_repository_name.azurecr.io -u $ACR_USERNAME -p $ACR_PASSWORD
docker build -f Dockerfile -t chat_service --platform=linux/amd64 .
docker tag chat_service:latest $TF_VAR_image_repository_name.azurecr.io/chat_service:$TF_VAR_image_tag
docker push $TF_VAR_image_repository_name.azurecr.io/chat_service:$TF_VAR_image_tag
check_exit_status

terraform init
terraform apply