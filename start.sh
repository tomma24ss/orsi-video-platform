#!/bin/bash

set -e  # Exit on error

echo "🚀 Starting Docker and k3s..."
sudo systemctl start docker
sudo systemctl start k3s

# Ensure Kubernetes config is accessible
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

echo "📂 Ensuring Host Directory for PV..."
# ✅ Create and ensure proper permissions for the host directory
sudo mkdir -p /data/k8s/videos
sudo chmod -R 777 /data/k8s/videos

echo "🔄 Building Docker Images using docker-compose..."
sudo docker compose build

echo "📦 Importing Docker Images into k3s..."
sudo docker save orsi-frontend:latest | sudo k3s ctr images import -
sudo docker save orsi-api | sudo k3s ctr images import -

echo "🧹 Cleaning up Old Kubernetes Resources..."
sudo kubectl delete -f ./k8s/api/deployment.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/api/service.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/frontend/deployment.yaml --ignore-not-found
sudo kubectl delete -f ./k8s/frontend/service.yaml --ignore-not-found
sudo kubectl delete pvc video-pvc --ignore-not-found
sudo kubectl delete pv video-pv --ignore-not-found

echo "⚙️  Applying Kubernetes Persistent Volume and Claim..."
sudo kubectl apply -f ./k8s/api/pv.yaml
sudo kubectl apply -f ./k8s/api/pvc.yaml

echo "⚙️  Applying API Deployment and Service to Trigger PVC Binding..."
sudo kubectl apply -f ./k8s/api/deployment.yaml
sudo kubectl apply -f ./k8s/api/service.yaml

echo "⏳ Waiting for PVC to be bound after pod is scheduled..."
while [[ $(kubectl get pvc video-pvc -o jsonpath='{.status.phase}') != "Bound" ]]; do
    echo "PVC is still pending...waiting for pod to trigger binding..."
    sleep 2
done
echo "✅ PVC is now bound!"

echo "⚙️  Applying Frontend Deployment and Service..."
sudo kubectl apply -f ./k8s/frontend/deployment.yaml
sudo kubectl apply -f ./k8s/frontend/service.yaml

echo "🔍 Checking Kubernetes Resources..."
sudo kubectl get pv
sudo kubectl get pvc
sudo kubectl get pods
sudo kubectl get services

echo "✅ Startup Complete! Access the app via WSL2 IP or localhost (if port-proxy is configured)."
