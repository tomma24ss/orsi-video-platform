from flask import Blueprint, request, jsonify, send_from_directory
from services.video_service import VideoService
from exceptions.api_exceptions import APIException
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
import os
import uuid
import json

video_blueprint = Blueprint('video', __name__, url_prefix='/videos')
logger = logging.getLogger(__name__)

# Directories
UPLOAD_FOLDER = "/data/videos/uploaded"
PROCESSED_FOLDER = "/data/videos/processed"
METADATA_FOLDER = "/data/videos/metadata"
STATUS_FOLDER = "/data/videos/status"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)
os.makedirs(STATUS_FOLDER, exist_ok=True)

# Initialize Kubernetes configuration inside the container
try:
    config.load_incluster_config()  # For Kubernetes Pods
except config.ConfigException:
    config.load_kube_config()  # For local development

k8s_batch = client.BatchV1Api()

# ✅ Trigger AI Job
def trigger_ai_job(unique_filename):
    job_id = str(uuid.uuid4())[:8]
    job_name = f"ai-job-{unique_filename.replace('.', '-')}-{job_id}"

    try:
        # Define the job manifest
        job = client.V1Job(
            metadata=client.V1ObjectMeta(name=job_name),
            spec=client.V1JobSpec(
                ttl_seconds_after_finished=120,
                backoff_limit=0,
                template=client.V1PodTemplateSpec(
                    metadata=client.V1ObjectMeta(labels={"app": "ai-job"}),
                    spec=client.V1PodSpec(
                        restart_policy="Never",
                        containers=[
                            client.V1Container(
                                name="ai-job",
                                image="orsi-ai-job:latest",
                                image_pull_policy="IfNotPresent",
                                env=[client.V1EnvVar(name="VIDEO_FILENAME", value=unique_filename)],
                                volume_mounts=[
                                    client.V1VolumeMount(
                                        name="video-storage",
                                        mount_path="/data/videos",
                                        read_only=False
                                    )
                                ]
                            )
                        ],
                        volumes=[
                            client.V1Volume(
                                name="video-storage",
                                persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                    claim_name="video-pvc",
                                    read_only=False
                                )
                            )
                        ]
                    )
                )
            )
        )
        k8s_batch.create_namespaced_job(namespace="default", body=job)
        logger.info(f"AI Job triggered successfully for {unique_filename}")
    except Exception as e:
        logger.error(f"Failed to trigger AI job: {e}")
        raise APIException(str(e), 500)

# ✅ Upload Raw Video
@video_blueprint.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        raise APIException("No file part in request.", 400)

    file = request.files['video']
    if file.filename == '':
        raise APIException("No selected file.", 400)

    try:
        unique_filename = VideoService.save_video(file, UPLOAD_FOLDER)
        trigger_ai_job(unique_filename)
        return jsonify({"message": f"File uploaded and AI job triggered for {unique_filename}"}), 200
    except Exception as e:
        raise APIException(str(e))

# ✅ Job Status Endpoint
@video_blueprint.route('/job-status/<filename>', methods=['GET'])
def job_status(filename):
    processed_file_path = os.path.join(PROCESSED_FOLDER, filename)
    if os.path.exists(processed_file_path):
        return jsonify({"status": "completed"})

    jobs = k8s_batch.list_namespaced_job(namespace="default", label_selector="app=ai-job")
    for job in jobs.items:
        if filename in job.metadata.name:
            return jsonify({"status": "processing"})
    
    return jsonify({"status": "not_found"})

# ✅ Job Progress Endpoint
@video_blueprint.route('/job-progress/<filename>', methods=['GET'])
def check_job_progress(filename):
    status_path = os.path.join(STATUS_FOLDER, f"{filename}.json")
    if os.path.exists(status_path):
        with open(status_path, "r") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"status": "not_started", "progress": 0})

# ✅ List Uploaded and Processed Videos
@video_blueprint.route('/', methods=['GET'])
def list_videos():
    try:
        uploaded = VideoService.list_videos(UPLOAD_FOLDER)
        processed = VideoService.list_videos(PROCESSED_FOLDER)
        return jsonify({"uploaded": uploaded, "processed": processed})
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise APIException(str(e))

# ✅ Serve Uploaded, Processed Video or Metadata
@video_blueprint.route('/<folder>/<filename>', methods=['GET'])
def get_video(folder, filename):
    try:
        folder_map = {
            "uploaded": UPLOAD_FOLDER,
            "processed": PROCESSED_FOLDER,
            "metadata": METADATA_FOLDER
        }

        if folder not in folder_map:
            raise APIException("Invalid folder name.", 400)

        mime_type = 'application/json' if folder == "metadata" else 'video/mp4'
        return send_from_directory(folder_map[folder], filename, mimetype=mime_type)
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise APIException(str(e))

# ✅ Delete Video or Metadata
@video_blueprint.route('/<folder>/<filename>', methods=['DELETE'])
def delete_video(folder, filename):
    try:
        folder_map = {
            "uploaded": UPLOAD_FOLDER,
            "processed": PROCESSED_FOLDER,
            "metadata": METADATA_FOLDER
        }

        if folder not in folder_map:
            raise APIException("Invalid folder name.", 400)

        VideoService.delete_video(filename, folder_map[folder])
        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise APIException(str(e))
