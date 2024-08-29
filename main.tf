# main.tf - Terraform script for AKS Cluster with heterogeneous instance types

provider "azurerm" {
  features {}
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
  name                = "pool1"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id
  vm_size             = "Standard_DS3_v2"  # Change this to another instance type
  node_count          = 1
  max_pods            = 30
  os_type             = "Linux"
  mode                = "User"
  enable_auto_scaling = false
}

# Additional Node Pool 2
resource "azurerm_kubernetes_cluster_node_pool" "pool_2" {
  name                = "pool2"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.aks_cluster.id
  vm_size             = "Standard_F4s_v2"  # Another different instance type
  node_count          = 1
  max_pods            = 30
  os_type             = "Linux"
  mode                = "User"
  enable_auto_scaling = false
}

# Output Kubernetes Config
output "kube_config" {
  value = azurerm_kubernetes_cluster.aks_cluster.kube_config_raw
}

# Helm deployment of the service on each node pool using node selector
resource "helm_release" "chat_service_default" {
  name       = "chat-service-default"
  repository = "https://charts.bitnami.com/bitnami"  # Update if your Helm chart repository is different
  chart      = "chat-service-chart"                 # Replace with your actual chart name

  set {
    name  = "image.repository"
    value = "deterministicchatservicee.azurecr.io/your-service-image"  # Set your image path
  }

  set {
    name  = "replicaCount"
    value = "1"
  }

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "nodeSelector.nodepool"
    value = "default"
  }

  depends_on = [azurerm_kubernetes_cluster.aks_cluster]
}

resource "helm_release" "chat_service_pool1" {
  name       = "chat-service-pool1"
  repository = "https://charts.bitnami.com/bitnami"  # Update if your Helm chart repository is different
  chart      = "chat-service-chart"                 # Replace with your actual chart name

  set {
    name  = "image.repository"
    value = "deterministicchatservicee.azurecr.io/your-service-image"  # Set your image path
  }

  set {
    name  = "replicaCount"
    value = "1"
  }

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "nodeSelector.nodepool"
    value = "pool1"
  }

  depends_on = [azurerm_kubernetes_cluster_node_pool.pool_1]
}

resource "helm_release" "chat_service_pool2" {
  name       = "chat-service-pool2"
  repository = "https://charts.bitnami.com/bitnami"  # Update if your Helm chart repository is different
  chart      = "chat-service-chart"                 # Replace with your actual chart name

  set {
    name  = "image.repository"
    value = "deterministicchatservicee.azurecr.io/your-service-image"  # Set your image path
  }

  set {
    name  = "replicaCount"
    value = "1"
  }

  set {
    name  = "service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "nodeSelector.nodepool"
    value = "pool2"
  }

  depends_on = [azurerm_kubernetes_cluster_node_pool.pool_2]
}
