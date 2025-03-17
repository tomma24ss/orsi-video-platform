from flask import Blueprint, request, jsonify, send_from_directory
from services.video_service import VideoService
from exceptions.api_exceptions import APIException
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
import os
import uuid

video_blueprint = Blueprint('video', __name__, url_prefix='/videos')
logger = logging.getLogger(__name__)

# Directories
UPLOAD_FOLDER = "/data/videos/uploaded"
PROCESSED_FOLDER = "/data/videos/processed"
METADATA_FOLDER = "/data/videos/metadata"

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)

# Initialize Kubernetes configuration inside the container
try:
    config.load_incluster_config()  # For Kubernetes Pods
except config.ConfigException:
    config.load_kube_config()  # For local development

k8s_batch = client.BatchV1Api()

# Trigger AI Job
def trigger_ai_job(unique_filename):
    job_id = str(uuid.uuid4())[:8]
    job_name = f"ai-job-{unique_filename.replace('.', '-')}-{job_id}"

    try:
        # Delete existing job if it exists
        k8s_batch.delete_namespaced_job(
            name=job_name,
            namespace="default",
            body=client.V1DeleteOptions(propagation_policy='Foreground')
        )
        logger.info(f"Existing job '{job_name}' deleted successfully.")
    except ApiException as e:
        if e.status != 404:
            logger.error(f"Failed to delete existing job '{job_name}': {e}")
            raise

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

    try:
        k8s_batch.create_namespaced_job(namespace="default", body=job)
        logger.info(f"AI Job triggered successfully for {unique_filename}")
    except Exception as e:
        logger.error(f"Failed to trigger AI job: {e}")
        raise APIException(str(e), 500)

# Upload Raw Video
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

# List Uploaded and Processed Videos
@video_blueprint.route('/', methods=['GET'])
def list_videos():
    try:
        uploaded = VideoService.list_videos(UPLOAD_FOLDER)
        processed = VideoService.list_videos(PROCESSED_FOLDER)
        return jsonify({"uploaded": uploaded, "processed": processed})
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise APIException(str(e))

# Serve Uploaded, Processed Video or Metadata
@video_blueprint.route('/<folder>/<filename>', methods=['GET'])
def get_video(folder, filename):
    try:
        if folder == "uploaded":
            return send_from_directory(UPLOAD_FOLDER, filename, mimetype='video/mp4')
        elif folder == "processed":
            return send_from_directory(PROCESSED_FOLDER, filename, mimetype='video/mp4')
        elif folder == "metadata":
            return send_from_directory(METADATA_FOLDER, filename, mimetype='application/json')
        else:
            raise APIException("Invalid folder name.", 400)
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        raise APIException(str(e))

# Delete Video or Metadata
@video_blueprint.route('/<folder>/<filename>', methods=['DELETE'])
def delete_video(folder, filename):
    try:
        if folder == "uploaded":
            VideoService.delete_video(filename, UPLOAD_FOLDER)
        elif folder == "processed":
            VideoService.delete_video(filename, PROCESSED_FOLDER)
        elif folder == "metadata":
            VideoService.delete_video(filename, METADATA_FOLDER)
        else:
            raise APIException("Invalid folder name.", 400)

        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise APIException(str(e))
