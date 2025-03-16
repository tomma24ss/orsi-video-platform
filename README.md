# 🎬 Orsi Video Platform

A minimal video platform built with:

- **Frontend**: React (TypeScript)  
- **Backend**: Python Flask API  
- **AI Processing**: (Optional, for future phases)  
- **Infrastructure**: Docker, Kubernetes (k3s)

---

## 🚀 Features

- 📤 Upload videos
- 🎥 Watch uploaded videos
- 🗑️ Delete videos
- 🧠 Display AI-generated metadata (to be integrated)
- 💾 Persistent storage using Kubernetes PV & PVC

---

## 📚 Project Architecture

```
orsi-video-platform/
├── api/                # Flask API for video operations
├── frontend/           # React frontend (TypeScript)
├── k8s/                # Kubernetes deployment and service files
│   ├── api/            # API Kubernetes manifests
│   └── frontend/       # Frontend Kubernetes manifests
├── start.sh          # Script to start Docker and Kubernetes deployments
├── stop.sh             # Script to clean and stop Docker and Kubernetes deployments
└── README.md           # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. **Clone the Repository**

```bash
git clone https://github.com/<your-username>/orsi-video-platform.git
cd orsi-video-platform
```

### 2. **Ensure Dependencies are Installed**

- **Docker**
- **k3s** (Lightweight Kubernetes)
- **kubectl** (for interacting with Kubernetes)
- **Python (3.12+)** for the Flask API

---

## 🚀 Deployment Instructions

### 1. **Start the platform deployment**

```bash
./start.sh
```

This script will:

- Start Docker and k3s.
- Build Docker images for both the API and frontend.
- Import the Docker images into k3s.
- Apply Kubernetes manifests for PV, PVC, deployments, and services.
- Display the status of all Kubernetes resources.

---

### 2. **Access the Platform**

- **Frontend**: [http://WSL2-IP:30001/](http://<WSL2-IP>:30001/)  
- **API**: [http://WSL2-IP:30002/videos](http://<WSL2-IP>:30002/videos)

---

### 3. **Stop and remove the platform deployment**

```bash
./stop.sh
```

This script will:

- Stop all Kubernetes deployments and services.
- Remove persistent volumes and claims.
- Clean up Docker containers, volumes, and images.
- Stop Docker and k3s services.

---

## 🛠️ Development Instructions

### Frontend (React)

```bash
cd frontend/frontend-app
npm install
npm start
```

- Runs the frontend in development mode.  
- Accessible at [http://localhost:3000](http://localhost:3000).

---

### Backend (Flask API)

```bash
cd api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

- Runs the API in development mode on [http://localhost:5000](http://localhost:5000).

---

### ✅ Environment Variables (Optional)

In development mode, you can create a `.env` file in the `api` directory to specify custom configurations.

**Example `.env` file:**

```env
UPLOAD_FOLDER=/absolute/path/to/local/videos
CORS_ORIGINS=http://localhost:3000
```

> **Note**: In Kubernetes, the `UPLOAD_FOLDER` is automatically set via volume mounts, so you don't need to set it manually.

---

## 📦 Kubernetes Details

### Persistent Volume (PV) and Persistent Volume Claim (PVC)

- **Host Path**: Video data is persisted at `/data/k8s/videos` on the host system.  
- **Container Path**: Inside the API container, it's accessible as `/data/videos`.
  
- **Why `/data/videos`?**  
  - Kubernetes automatically mounts the host directory into the container, ensuring persistence.  
  - The API only needs to save files to `/data/videos` (which maps to the persistent storage).

### Volume Example

- **Host Path**: `/data/k8s/videos`  
- **Container Path**: `/data/videos`

---

### Deployment Files

- **API Kubernetes Files**:  
  `./k8s/api/pv.yaml`, `./k8s/api/pvc.yaml`, `./k8s/api/deployment.yaml`, `./k8s/api/service.yaml`

- **Frontend Kubernetes Files**:  
  `./k8s/frontend/deployment.yaml`, `./k8s/frontend/service.yaml`

---

## 📝 Usage Instructions

1. **Uploading Videos**

- Use the frontend to upload `.mp4` files.
- The API will automatically rename files if duplicates exist (e.g., `video.mp4` -> `video_2.mp4`).

2. **Viewing Videos**

- Uploaded videos will be listed and can be played directly in the frontend.

3. **Deleting Videos**

- Use the frontend to delete any video.

---

## 🧹 Cleanup Instructions

If any resources need to be cleaned manually:

```bash
kubectl delete all --all --ignore-not-found
kubectl delete pvc --all --ignore-not-found
kubectl delete pv --all --ignore-not-found
sudo docker system prune -f
```

---

## ⚡ Known Issues

- CORS issues may occur if accessing from a different origin. Ensure CORS settings in the API are updated accordingly.
- For local development, ensure Docker and k3s are properly started.

---

## 👨‍💻 Contributing

1. Fork this repository.
2. Create a new branch for your feature.
3. Commit your changes with clear messages.
4. Submit a pull request for review.

---


## 🤝 Acknowledgements

- [Docker](https://www.docker.com/)  
- [K3s](https://k3s.io/)  
- [React](https://reactjs.org/)  
- [Flask](https://flask.palletsprojects.com/)

---

## ✅ **How to Use This**

1. Replace `<your-username>` in the GitHub clone URL.  
2. Adjust the `<WSL2-IP>` with your actual WSL2 IP address.  
3. Ensure all folder structures match as described.  
4. Test the setup by running:

```bash
chmod +x start.sh
./start.sh
```

---