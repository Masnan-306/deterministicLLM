terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.74.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = "36577d1d-abda-49a6-86c8-67d9341c45a5"
}

# Resource group for AKS
resource "azurerm_resource_group" "aks_rg" {
  name     = "aksResourceGroup"
  location = var.location
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "aks_cluster" {
  name                = "aksCluster"
  location            = azurerm_resource_group.aks_rg.location
  resource_group_name = azurerm_resource_group.aks_rg.name
  dns_prefix          = "aksk8s"

  default_node_pool {
    name       = "default"
    node_count = 3
    vm_size    = "Standard_DS2_v2"
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
  config_path = local_file.kubeconfig.filename
}

# Configure Helm provider using the same kubeconfig
provider "helm" {
  kubernetes {
    config_path = local_file.kubeconfig.filename
  }
}

# Save kubeconfig to a local file to use with Kubernetes and Helm providers
resource "local_file" "kubeconfig" {
  content  = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
  filename = var.kube_config_path
  file_permission = "0600"
}

# Null resource to trigger secret recreation
resource "null_resource" "force_recreate" {
  # This trigger will update every time Terraform applies, causing the null_resource to always run
  triggers = {
    always_run = timestamp()
  }
}

# Kubernetes secret for ACR authentication
resource "kubernetes_secret" "acr_auth" {
  metadata {
    name      = "acr-auth-secret"
    namespace = "default"
  }

  type = "kubernetes.io/dockerconfigjson"

  data = {
    ".dockerconfigjson" = jsonencode({
      auths = {
        "${var.image_repository_name}.azurecr.io" = {
          "username" = var.acr_username
          "password" = var.acr_password
          "email"    = var.acr_email
          "auth"     = base64encode("${var.acr_username}:${var.acr_password}")
        }
      }
    })
  }

  # This ensures the secret is recreated whenever the null_resource changes
  depends_on = [null_resource.force_recreate]

  lifecycle {
    create_before_destroy = true
  }
}



# Helm deployment of the service on default node pool using the local chart
# resource "helm_release" "chat_service_default" {
#   name  = "chat-service"
#   chart = "./chat-service"  # Path to your local Helm chart

#   set {
#     name  = "image.repository"
#     value = "${var.image_repository_name}.azurecr.io/chat_service"
#   }

#   set {
#     name  = "image.tag"
#     value = var.image_tag
#   }

#   set {
#     name  = "imagePullSecret"
#     value = var.image_pull_secret
#   }

#   set {
#     name  = "replicaCount"
#     value = var.replica_count
#   }

#   set {
#     name  = "service.type"
#     value = var.service_type
#   }

#   set {
#     name  = "service.port"
#     value = var.service_port
#   }

#   set {
#     name  = "service.targetPort"
#     value = var.service_target_port
#   }

#   set {
#     name  = "nodeSelector.agentpool"
#     value = var.node_selector_agentpool
#   }

#   depends_on = [azurerm_kubernetes_cluster.aks_cluster, local_file.kubeconfig]
# }