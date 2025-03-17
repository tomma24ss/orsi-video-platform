#!/bin/bash

set -e  # Exit on error

echo "🛑 Stopping the Orsi Video Platform..."

# Define KUBECONFIG
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# Stop Kubernetes Deployments and Services
echo "🧹 Cleaning up Kubernetes Resources..."

# Delete AI Job
sudo kubectl delete -f ./k3s/ai-job/job.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# Delete Frontend Resources
sudo kubectl delete -f ./k3s/frontend/service.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/frontend/deployment.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# Delete API Resources
sudo kubectl delete -f ./k3s/api/service.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/api/deployment.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/api/rbac.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
# sudo kubectl delete -f ./k3s/api/pvc.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
# sudo kubectl delete -f ./k3s/api/pv.yaml --ignore-not-found --kubeconfig=$KUBECONFIG


# Stop Docker Containers
echo "🛑 Stopping Docker containers..."
sudo docker ps -q --filter "ancestor=orsi-frontend" --filter "ancestor=orsi-api" --filter "ancestor=orsi-ai-job" | xargs -r sudo docker stop

# Remove Docker Containers
echo "🧹 Removing Docker containers..."
sudo docker ps -a -q --filter "ancestor=orsi-frontend" --filter "ancestor=orsi-api" --filter "ancestor=orsi-ai-job" | xargs -r sudo docker rm

# Remove Docker Images (Optional)
echo "🗑️ Removing Docker images (if desired)..."
sudo docker rmi -f orsi-frontend:latest orsi-api:latest orsi-ai-job:latest || true

# Stop k3s and Docker services
echo "🛑 Stopping k3s and Docker services..."
sudo systemctl stop k3s
sudo systemctl stop docker

echo "✅ All services and containers have been stopped and cleaned up."
