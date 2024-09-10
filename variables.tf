
# Variables for Helm values
variable "image_repository_name" {
  description = "Docker image repository"
  default     = "deterministicchatservicee"
}

variable "image_tag" {
  description = "Docker image tag"
  default     = "v1.0"
}

variable "image_pull_secret" {
  description = "Kubernetes secret for ACR authentication"
  default     = "acr-auth-secret"
}

variable "replica_count" {
  description = "Number of replicas for the service"
  default     = 1
}

variable "service_type" {
  description = "Service type for Kubernetes (e.g., LoadBalancer, ClusterIP)"
  default     = "LoadBalancer"
}

variable "service_port" {
  description = "Port on which the service is exposed"
  default     = 80
}

variable "service_target_port" {
  description = "Port on the container to which the service forwards traffic"
  default     = 8000
}

variable "node_selector_agentpool" {
  description = "Node selector label for Kubernetes"
  default     = "default"
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

variable "location" {
  description = "Location for Azure resources"
  default     = "East US"
}

variable "kube_config_path" {
  description = "Kubernetes config file path"
  default     = "~/.kube/config"
}
