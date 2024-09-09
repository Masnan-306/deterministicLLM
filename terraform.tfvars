# Kubernetes secret for image pull
image_pull_secret = "acr-auth-secret"

# Replica count for the service
replica_count = 1

# Service configuration
service_type        = "LoadBalancer"  # Type of Kubernetes service (LoadBalancer, ClusterIP, NodePort)
service_port        = 80              # Port exposed by the service
service_target_port = 8000            # Port on the container to forward traffic

# Node selector for agent pool
node_selector_agentpool = "default"   # Node pool label for the deployment
