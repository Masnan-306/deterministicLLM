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

# Output Kubernetes Config
output "kube_config" {
  sensitive = true
  value     = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
}

# Configure Kubernetes provider using the kubeconfig
provider "kubernetes" {
  config_path = "/Users/zhinanwang/.kube_config.yaml"
}

# Configure Helm provider using the same kubeconfig
provider "helm" {
  kubernetes {
    config_path = "/Users/zhinanwang/.kube_config.yaml"
  }
}

# Save kubeconfig to a local file to use with Kubernetes and Helm providers
resource "local_file" "kubeconfig" {
  content  = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
  filename = "/Users/zhinanwang/.kube_config.yaml"
}

# Helm deployment of the service on default node pool using the local chart
resource "helm_release" "chat_service_default" {
  name  = "chat-service-default"
  chart = "./chat-service"  # Path to your local Helm chart

  set {
    name  = "nodeSelector.agentpool"
    value = "default"
  }

  depends_on = [azurerm_kubernetes_cluster.aks_cluster, local_file.kubeconfig]
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