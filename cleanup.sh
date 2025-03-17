#!/bin/bash

set -e  # Exit on error

# Set kubeconfig variable
KUBECONFIG="/etc/rancher/k3s/k3s.yaml"

echo "🛑 Stopping Kubernetes Deployments and Services..."

# ✅ Delete Frontend and API Deployments and Services
sudo kubectl delete -f ./k3s/frontend/deployment.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/frontend/service.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/api/deployment.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete -f ./k3s/api/service.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# ✅ Delete AI Job (Optional as it's managed by API)
sudo kubectl delete -f ./k3s/ai-job/job.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# # ✅ Delete Persistent Volumes and Claims
# sudo kubectl delete -f ./k3s/api/pv.yaml --ignore-not-found --kubeconfig=$KUBECONFIG
# sudo kubectl delete -f ./k3s/api/pvc.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

# ✅ Delete Kubernetes RBAC (if exists)
sudo kubectl delete -f ./k3s/api/rbac.yaml --ignore-not-found --kubeconfig=$KUBECONFIG

echo "🧹 Cleaning Up Host Directory for PV..."
# Remove all data in the volume directory
sudo rm -rf /data/k3s/videos/* || true

# ✅ Delete Remaining Kubernetes Resources
sudo kubectl delete all --all --ignore-not-found --kubeconfig=$KUBECONFIG
# sudo kubectl delete pvc --all --ignore-not-found --kubeconfig=$KUBECONFIG
# sudo kubectl delete pv --all --ignore-not-found --kubeconfig=$KUBECONFIG
sudo kubectl delete jobs --all --ignore-not-found --kubeconfig=$KUBECONFIG



echo "🧹 Cleaning Up Docker Containers, Images, and Volumes..."

# ✅ Stop Docker containers and clean up
sudo docker compose down --volumes --remove-orphans
sudo docker system prune -af
sudo docker volume prune -f
sudo docker image prune -af

# ✅ Remove all Docker images (if any)
sudo docker rmi $(sudo docker images -q) --force || true

echo "🧹 Cleaning Up k3s Images..."
# ✅ Remove all k3s images
sudo k3s ctr images ls -q | xargs -r sudo k3s ctr images rm || true

# ✅ Stop and Reset k3s to remove any residuals
echo "🛑 Resetting k3s cluster..."
sudo k3s-killall.sh || true
sudo k3s-uninstall.sh || true

# Optional: Remove leftover k3s directories if necessary
sudo rm -rf /etc/rancher/k3s
sudo rm -rf /var/lib/rancher/k3s
sudo rm -rf /var/lib/kubelet

echo "🔍 Verifying Docker and Kubernetes Cleanup..."
sudo docker ps -a
sudo docker images
sudo kubectl get all --kubeconfig=$KUBECONFIG || echo "✅ No Kubernetes resources found (as expected)."

echo "🛑 Stopping Docker and Cleaning Up System Services..."
sudo systemctl stop k3s || true
sudo systemctl stop docker || true

echo "✅ Complete Cleanup and Shutdown of Docker and k3s is done!"
