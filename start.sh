#!/bin/bash

set -e  # Exit on error

echo "⚙️ Checking and Installing Required Tools..."

# Function to install a package if not already installed
install_if_missing() {
    if ! command -v "$1" &> /dev/null; then
        echo "🔄 Installing $1..."
        sudo apt-get update
        sudo apt-get install -y "$2"
    else
        echo "✅ $1 is already installed."
    fi
}

# Install required tools
install_if_missing "pv" "pv"
install_if_missing "docker" "docker.io"

# Install k3s if not exists
if ! command -v k3s &> /dev/null; then
    echo "🔄 Installing k3s..."
    curl -sfL https://get.k3s.io | sh -
else
    echo "✅ k3s is already installed."
fi

# Install kubectl if not exists
if ! command -v kubectl &> /dev/null; then
    echo "🔄 Installing kubectl..."
    sudo apt-get update
    sudo apt-get install -y kubectl
else
    echo "✅ kubectl is already installed."
fi

echo "🚀 Starting Docker and k3s..."
sudo systemctl start docker
sudo systemctl start k3s

# Ensure Kubernetes config is accessible and set the environment variable
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Wait for the k3s API server to be accessible
echo "⏳ Waiting for k3s API server to be accessible..."
until kubectl cluster-info --kubeconfig=$KUBECONFIG &> /dev/null; do
    echo "Waiting for Kubernetes API server to be accessible..."
    sleep 5
done
echo "✅ Kubernetes API server is accessible."

# Wait for the node to be Ready
echo "⏳ Waiting for k3s node to be Ready..."
until kubectl get nodes --kubeconfig=$KUBECONFIG --no-headers | grep -q ' Ready '; do
    echo "Node is not ready yet...waiting."
    sleep 5
done
echo "✅ Kubernetes node is Ready!"

# Ensure Host Directory for PV
echo "📂 Ensuring Host Directory for PV..."
sudo mkdir -p /data/k8s/videos
sudo chmod -R 777 /data/k8s/videos

# Build Docker Images
echo "🔄 Building Docker Images using docker-compose..."
sudo docker compose build

# Verify Docker images are built
for image in orsi-frontend orsi-api orsi-ai-job; do
    if ! sudo docker image inspect "$image:latest" > /dev/null 2>&1; then
        echo "❌ Docker image $image:latest not found. Build failed!"
        exit 1
    fi
done

# Import Docker Images into k3s
echo "📦 Importing Docker Images into k3s..."
for image in orsi-frontend orsi-api orsi-ai-job; do
    echo "🔄 Importing $image..."
    sudo docker save "$image:latest" | sudo k3s ctr images import -
done

# Clean up Old Kubernetes Resources
echo "🧹 Cleaning up Old Kubernetes Resources..."
for resource in deployment.yaml service.yaml; do
    sudo kubectl delete -f ./k3s/api/$resource --ignore-not-found --kubeconfig=$KUBECONFIG
    sudo kubectl delete -f ./k3s/frontend/$resource --ignore-not-found --kubeconfig=$KUBECONFIG
done
sudo kubectl delete -f ./k3s/ai-job/job.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# # Wait for PVC/PV to terminate
# echo "⏳ Waiting for PVC/PV to be deleted..."
# while kubectl get pvc video-pvc --kubeconfig=$KUBECONFIG &> /dev/null || kubectl get pv video-pv --kubeconfig=$KUBECONFIG &> /dev/null; do
#     echo "PVC/PV still terminating...waiting."
#     sleep 2
# done
# echo "✅ Old PVC/PV resources cleaned."

# Apply Kubernetes Persistent Volume and Claim
echo "⚙️  Applying Kubernetes Persistent Volume and Claim..."
sudo kubectl apply -f ./k3s/api/pv.yaml --kubeconfig=$KUBECONFIG
sudo kubectl apply -f ./k3s/api/pvc.yaml --kubeconfig=$KUBECONFIG

# Apply Kubernetes RBAC for API
echo "⚙️  Applying Kubernetes RBAC for API..."
sudo kubectl apply -f ./k3s/api/rbac.yaml --kubeconfig=$KUBECONFIG

# Apply API Deployment and Service
echo "⚙️  Applying API Deployment and Service..."
sudo kubectl apply -f ./k3s/api/deployment.yaml --kubeconfig=$KUBECONFIG
sudo kubectl apply -f ./k3s/api/service.yaml --kubeconfig=$KUBECONFIG

# Wait for API pod to be ready
echo "⏳ Waiting for API pod to be ready..."
until kubectl get pods -l app=api --kubeconfig=$KUBECONFIG -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; do
    echo "API pod is not ready yet..."
    sleep 5
done
echo "✅ API pod is now running!"

# Apply Frontend Deployment and Service
echo "⚙️  Applying Frontend Deployment and Service..."
sudo kubectl apply -f ./k3s/frontend/deployment.yaml --kubeconfig=$KUBECONFIG
sudo kubectl apply -f ./k3s/frontend/service.yaml --kubeconfig=$KUBECONFIG

# Wait for Frontend pod to be ready
echo "⏳ Waiting for Frontend pod to be ready..."
until kubectl get pods -l app=frontend --kubeconfig=$KUBECONFIG -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; do
    echo "Frontend pod is not ready yet..."
    sleep 5
done
echo "✅ Frontend pod is now running!"

# Final Check
echo "🔍 Final Kubernetes Resources Check..."
kubectl get pv --kubeconfig=$KUBECONFIG
kubectl get pvc --kubeconfig=$KUBECONFIG
kubectl get pods --kubeconfig=$KUBECONFIG
kubectl get services --kubeconfig=$KUBECONFIG

echo "✅ Startup Complete! Access the app via WSL2 IP or localhost (if port-proxy is configured)."
