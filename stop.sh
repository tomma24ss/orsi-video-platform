#!/bin/bash

set -e  # Exit on error

echo "🛑 Stopping Kubernetes Deployments and Services..."

# ✅ Delete Frontend and API Deployments and Services
sudo kubectl delete -f ./k8s/frontend/deployment.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/frontend/service.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/api/deployment.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/api/service.yaml --ignore-not-found

echo "🛑 Deleting Kubernetes Persistent Volumes and Claims..."

# ✅ Delete PVC and PV for API
sudo kubectl delete pvc video-pvc --ignore-not-found
sudo kubectl delete pv video-pv --ignore-not-found

echo "🧹 Cleaning Up Docker Containers and Images..."

# ✅ Clean up Docker containers, volumes, and images
sudo docker compose down --volumes --remove-orphans
sudo docker system prune -f
sudo docker volume prune -f
sudo docker image prune -f

echo "🧹 Cleaning Up Kubernetes Residuals..."

# ✅ Check if any resources are still running
sudo kubectl get all
sudo kubectl get pvc
sudo kubectl get pv

echo "🔍 Verifying Docker Cleanup..."
sudo docker ps -a
sudo docker images

echo "🧹 Cleaning Up Host Directory for PV (Optional)..."
# Uncomment the next line if you want to clean up the host directory too
# sudo rm -rf /data/k8s/videos

echo "🛑 Stopping Docker and k3s Services..."
sudo systemctl stop k3s
sudo systemctl stop docker

echo "✅ Cleanup and Shutdown Complete!"
