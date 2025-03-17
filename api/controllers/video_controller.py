from flask import Blueprint, request, jsonify
from services.video_service import VideoService
from exceptions.api_exceptions import APIException
from kubernetes import client, config
from kubernetes.client.rest import ApiException
import logging
import os
import uuid

video_blueprint = Blueprint('video', __name__, url_prefix='/videos')
logger = logging.getLogger(__name__)


# Initialize Kubernetes configuration inside the container
try:
    config.load_incluster_config()  # For Kubernetes Pods
except config.ConfigException:
    config.load_kube_config()  # For local development

k8s_batch = client.BatchV1Api()


def trigger_ai_job(unique_filename):
    job_id = str(uuid.uuid4())[:8]  # Generate a short unique ID
    job_name = f"ai-job-{unique_filename.replace('.', '-')}-{job_id}"
    
    # First, delete any existing job with the same name (Failed or Running)
    try:
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
            ttl_seconds_after_finished=120,  # Auto-delete after 60 seconds
            backoff_limit=0,
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={"app": "ai-job"},
                    owner_references=[
                        client.V1OwnerReference(
                            api_version="batch/v1",
                            kind="Job",
                            name=job_name,
                            uid="",
                            controller=True,
                            block_owner_deletion=True
                        )
                    ]
                ),
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
                                    mount_path="/data/videos"
                                )
                            ]
                        )
                    ],
                    volumes=[
                        client.V1Volume(
                            name="video-storage",
                            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                                claim_name="video-pvc"
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

# List Videos
@video_blueprint.route('/', methods=['GET'])
def list_videos():
    try:
        videos = VideoService.list_videos()
        return jsonify(videos)
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        raise APIException(str(e))

# Upload Video Route
@video_blueprint.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        raise APIException("No file part in request.", 400)

    file = request.files['video']
    if file.filename == '':
        raise APIException("No selected file.", 400)

    try:
        unique_filename = VideoService.save_video(file)

        # Trigger AI Job after upload
        trigger_ai_job(unique_filename)

        return jsonify({"message": f"File uploaded and AI job triggered for {unique_filename}"}), 200
    except Exception as e:
        raise APIException(str(e))
    
# Serve Video
@video_blueprint.route('/<filename>', methods=['GET'])
def get_video(filename):
    try:
        return VideoService.get_video(filename)
    except Exception as e:
        logger.error(f"Error serving video: {e}")
        raise APIException(str(e))

# Delete Video
@video_blueprint.route('/<filename>', methods=['DELETE'])
def delete_video(filename):
    try:
        VideoService.delete_video(filename)
        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise APIException(str(e))
