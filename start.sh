#!/bin/bash

set -e  # Exit on error

echo "⚙️ Checking and Installing Required Tools..."

# Function to install a package if not already installed
install_if_missing() {
    if ! dpkg -l | grep -qw "$2"; then
        echo "🔄 Installing $1..."
        sudo apt-get update
        sudo apt-get install -y "$2"
    else
        echo "✅ $1 is already installed."
    fi
}
install_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo "🔄 Installing kubectl..."

        # Add Kubernetes apt repository key
        sudo apt-get update
        sudo apt-get install -y apt-transport-https ca-certificates curl

        curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo tee /usr/share/keyrings/kubernetes-archive-keyring.gpg > /dev/null

        echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://packages.cloud.google.com/apt kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list

        # Install kubectl
        sudo apt-get update
        sudo apt-get install -y kubectl
    else
        echo "✅ kubectl is already installed."
    fi
}
# Function to install Docker manually (without Docker Desktop)
install_docker() {
    echo "🔍 Checking Docker installation..."
    
    # Check if Docker is installed and running
    if command -v docker &> /dev/null && systemctl is-active --quiet docker; then
        echo "✅ Docker is already installed and running."
        return
    fi

    echo "🔄 Installing Docker..."

    # Remove any old versions
    sudo apt-get remove -y docker docker-engine docker.io containerd runc || true
    sudo apt-get update

    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker’s official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo tee /etc/apt/keyrings/docker.asc > /dev/null

    # Add Docker repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io

    # Enable and start Docker service
    echo "🚀 Enabling and starting Docker service..."
    sudo systemctl enable --now docker || {
        echo "⚠️ systemd is not running. Manually starting Docker..."
        sudo dockerd &
        sleep 5
    }

    # Verify Docker installation
    if ! systemctl is-active --quiet docker; then
        echo "❌ Docker failed to start. Please check logs."
        exit 1
    fi

    echo "✅ Docker installation complete."
}

# Ensure systemd is running in WSL
ensure_systemd() {
    if [ -d "/run/systemd/system" ]; then
        echo "✅ systemd is available."
    else
        echo "❌ systemd is not running in WSL. You must enable it manually."
        exit 1
    fi
}

# Detect if running inside WSL
if grep -qi microsoft /proc/version; then
    echo "💡 Running inside WSL. Installing Docker natively (without Docker Desktop)..."
    ensure_systemd
    install_docker
else
    echo "💡 Running on native Linux. Installing Docker normally..."
    install_docker
fi

# Install required tools
install_if_missing "pv" "pv"

# Install k3s if not exists
if ! command -v k3s &> /dev/null; then
    echo "🔄 Installing k3s..."
    curl -sfL https://get.k3s.io | sh -
else
    echo "✅ k3s is already installed."
fi

install_kubectl

# Start services properly
echo "🚀 Starting Docker and k3s..."
if systemctl list-units --full -all | grep -q "docker.service"; then
    sudo systemctl start docker
else
    echo "❌ Docker service not found! Installation failed."
    exit 1
fi
sudo systemctl start k3s || echo "⚠️ Failed to start k3s. Make sure k3s is installed correctly."

# Ensure Kubernetes config is accessible
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
sudo chmod 644 /etc/rancher/k3s/k3s.yaml

# Wait for k3s API server to be accessible
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

echo "✅ Startup Complete! Access the app via WSL2 IP or localhost."
# Get the WSL2 IP address
WSL_IP=$(hostname -I | awk '{print $1}')

# If the IP is empty, set a fallback message
if [[ -z "$WSL_IP" ]]; then
    WSL_IP="(IP could not be detected, use 'hostname -I' to check manually)"
fi

# Print the URLs where the services are running
echo -e "\n🚀 Application is running at:"
echo "Frontend: http://$WSL_IP:30001/"
echo "API: http://$WSL_IP:30002/videos"