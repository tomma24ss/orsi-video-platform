from flask import Blueprint, request, jsonify, send_from_directory
from services.video_service import VideoService
from exceptions.api_exceptions import APIException

video_blueprint = Blueprint('video', __name__, url_prefix='/videos')

# List Videos
@video_blueprint.route('/', methods=['GET'])
def list_videos():
    try:
        videos = VideoService.list_videos()
        return jsonify(videos)
    except Exception as e:
        raise APIException(str(e))

# Upload Video
@video_blueprint.route('/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        raise APIException("No file part in request.", 400)

    file = request.files['video']
    if file.filename == '':
        raise APIException("No selected file.", 400)

    try:
        unique_filename = VideoService.save_video(file)
        return jsonify({"message": f"File uploaded as {unique_filename}"}), 200
    except Exception as e:
        raise APIException(str(e))

# Serve Video
@video_blueprint.route('/<filename>', methods=['GET'])
def get_video(filename):
    try:
        return VideoService.get_video(filename)
    except Exception as e:
        raise APIException(str(e))

# Delete Video
@video_blueprint.route('/<filename>', methods=['DELETE'])
def delete_video(filename):
    try:
        VideoService.delete_video(filename)
        return jsonify({"message": "File deleted"}), 200
    except Exception as e:
        raise APIException(str(e))
