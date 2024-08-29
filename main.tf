# main.tf - Terraform script for AKS Cluster with heterogeneous instance types

provider "azurerm" {
  features {}
  subscription_id = "36577d1d-abda-49a6-86c8-67d9341c45a5"
}

# Resource group for AKS
resource "azurerm_resource_group" "aks_rg" {
  name     = "aksResourceGroup"
  location = "East US"
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                = "aksCluster"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  dns_prefix          = "aksk8s"

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_DS2_v2"  # Default node pool instance type
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    environment = "testing"
  }
}

# Additional Node Pool 1
resource "azurerm_kubernetes_cluster_node_pool" "pool_1" {
  name                   = "pool1"
  kubernetes_cluster_id  = azurerm_kubernetes_cluster.aks_cluster.id
  vm_size                = "Standard_DS3_v2"  # Change this to another instance type
  node_count             = 1
  max_pods               = 30
  os_type                = "Linux"
  mode                   = "User"
}

# Additional Node Pool 2
resource "azurerm_kubernetes_cluster_node_pool" "pool_2" {
  name                   = "pool2"
  kubernetes_cluster_id  = azurerm_kubernetes_cluster.aks_cluster.id
  vm_size                = "Standard_F4s_v2"  # Another different instance type
  node_count             = 1
  max_pods               = 30
  os_type                = "Linux"
  mode                   = "User"
}

# Output Kubernetes Config
output "kube_config" {
  sensitive = true
  value     = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
}

# Configure Kubernetes provider using the kubeconfig
provider "kubernetes" {
  config_path = "~/.kube_config.yaml"
}

# Configure Helm provider using the same kubeconfig
provider "helm" {
  kubernetes {
    config_path = "~/.kube_config.yaml"
  }
}

# Save kubeconfig to a local file to use with Kubernetes and Helm providers
resource "local_file" "kubeconfig" {
  content  = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
  filename = "~/.kube_config.yaml"
}
# Helm deployment of the service on default node pool using the local chart
resource "helm_release" "chat_service_default" {
  name  = "chat-service-default"
  chart = "./chat-service"  # Path to your local Helm chart

  set {
    name  = "nodeSelector.agentpool"
    value = "default"  # Matches the label for the default node pool
  }

  depends_on = [azurerm_kubernetes_cluster.aks_cluster, local_file.kubeconfig]
}

# Helm deployment of the service on pool1 node pool using the local chart
resource "helm_release" "chat_service_pool1" {
  name  = "chat-service-pool1"
  chart = "./chat-service"  # Path to your local Helm chart

  set {
    name  = "nodeSelector.agentpool"
    value = "pool1"  # Matches the label for node pool 1, assuming pool1 nodes are labeled similarly
  }

  depends_on = [azurerm_kubernetes_cluster_node_pool.pool_1, local_file.kubeconfig]
}

# Helm deployment of the service on pool2 node pool using the local chart
resource "helm_release" "chat_service_pool2" {
  name  = "chat-service-pool2"
  chart = "./chat-service"  # Path to your local Helm chart

  set {
    name  = "nodeSelector.agentpool"
    value = "pool2"  # Matches the label for node pool 2, assuming pool2 nodes are labeled similarly
  }

  depends_on = [azurerm_kubernetes_cluster_node_pool.pool_2, local_file.kubeconfig]
}

resource "kubernetes_secret" "acr_auth" {
  metadata {
    name      = "acr-auth-secret"
    namespace = "default"
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "deterministicchatservicee.azurecr.io" = {
          "username" = var.acr_username
          "password" = var.acr_password
          "email"    = var.acr_email
          "auth"     = base64encode("${var.acr_username}:${var.acr_password}")
        }
      }
    })
  }
}

variable "acr_username" {
  description = "Azure Container Registry username"
  sensitive   = true
}

variable "acr_password" {
  description = "Azure Container Registry password"
  sensitive   = true
}

variable "acr_email" {
  description = "Email associated with Azure Container Registry"
  sensitive   = true
}