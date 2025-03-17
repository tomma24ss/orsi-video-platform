# 🎬 Orsi Video Platform

A minimal video platform built with:

- **Frontend**: React (TypeScript)  
- **Backend**: Python Flask API  
- **AI Processing**: YOLO-based object detection  
- **Infrastructure**: Docker, Kubernetes (k3s)

---

## 🚀 Features

- 📤 Upload videos  
- 🎥 Watch uploaded and processed videos  
- ⚙️ Real-time progress bar for AI processing  
- 🧠 View AI-generated metadata for processed videos  
- 🗑️ Delete videos and metadata  
- 💾 Persistent storage using Kubernetes PV & PVC

---

## 📚 Project Architecture

```
orsi-video-platform/
├── api/                # Flask API for video operations and AI job management
├── ai-job/             # Python app for video processing with YOLO
├── frontend/           # React frontend (TypeScript)
├── k8s/                # Kubernetes deployment and service files
│   ├── api/            # API Kubernetes manifests
│   ├── frontend/       # Frontend Kubernetes manifests
│   └── ai-job/        # AI job Kubernetes manifest
├── start.sh            # Script to start Docker and Kubernetes deployments
├── stop.sh             # Script to clean and stop Docker and Kubernetes deployments
└── README.md           # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. **Clone the Repository**

```bash
git clone https://github.com/tomma24ss/orsi-video-platform.git
cd orsi-video-platform
```

### 2. **Ensure Dependencies are Installed**

- **Docker**  
- **k3s** (Lightweight Kubernetes)  
- **kubectl** (for interacting with Kubernetes)  
- **Python (3.12+)** for the Flask API  

---

## 🚀 Deployment Instructions

### 1. **Start the Platform Deployment**

```bash
./start.sh
```

This script will:

- Start Docker and k3s.  
- Build Docker images for the API, frontend, and AI job.  
- Import the Docker images into k3s.  
- Apply Kubernetes manifests for PV, PVC, deployments, and services.  
- Display the status of all Kubernetes resources.

---

### 2. **Access the Platform**

- **Frontend**: [http://WSL2-IP:30001/](http://<WSL2-IP>:30001/)  
- **API**: [http://WSL2-IP:30002/videos](http://<WSL2-IP>:30002/videos)

---

### 3. **Stop and Remove the Platform Deployment**

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

### AI Job (Video Processing)

```bash
cd ai-job
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

- Runs the AI job service for testing.

---

### ✅ Environment Variables (Optional)

In development mode, create a `.env` file in the `api` directory:

```env
export UPLOAD_FOLDER="/data/videos/uploaded"
export PROCESSED_FOLDER="/data/videos/processed"
export METADATA_FOLDER="/data/videos/metadata"
export CORS_ORIGINS="http://localhost:3000,http://172.19.245.152:30001"
```

> **Note**: In Kubernetes, these folders are set via volume mounts.

---

## 📦 Kubernetes Details

### Persistent Volume (PV) and Persistent Volume Claim (PVC)

- **Host Paths**:
  - Uploaded Videos: `/data/k8s/videos/uploaded`
  - Processed Videos: `/data/k8s/videos/processed`
  - Metadata: `/data/k8s/videos/metadata`

- **Container Paths**:
  - Uploaded: `/data/videos/uploaded`
  - Processed: `/data/videos/processed`
  - Metadata: `/data/videos/metadata`

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
   - Progress is shown in real-time while the AI job processes the video.

2. **Tracking AI Job Status**
   - A progress bar is displayed in the frontend for each uploaded video until processing is complete.

3. **Viewing Processed Videos**
   - Processed videos will appear automatically in the "Processed Videos" section.

4. **Viewing Metadata**
   - For each processed video, click on the **"View Metadata"** button to display AI-generated data.

5. **Deleting Videos or Metadata**
   - Use the frontend to delete any uploaded, processed video, or its metadata.

---

## 🧹 Cleanup Instructions

If resources need to be cleaned manually:

```bash
kubectl delete all --all --ignore-not-found
kubectl delete pvc --all --ignore-not-found
kubectl delete pv --all --ignore-not-found
sudo docker system prune -f
```

---

## ⚡ Known Issues

- **CORS**: Ensure CORS settings in the API are configured correctly for external access.
- **WSL2 IP**: If using WSL2, the IP may change after restarting, so update accordingly.
- **AI Job Delay**: The AI job may take up to 1 minute for larger videos.

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
- [Ultralytics YOLO](https://docs.ultralytics.com/)

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
