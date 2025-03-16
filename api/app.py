from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import logging

app = Flask(__name__)

# Explicitly allow the frontend origins
CORS(app, resources={r"/videos/*": {"origins": ["http://172.19.245.152:30001", "http://localhost:3000"]}}, supports_credentials=True)

UPLOAD_FOLDER = '/data/videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/videos', methods=['GET'])
def list_videos():
    try:
        videos = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.mp4')]
        logger.info(f"Listing videos: {videos}")
        return jsonify(videos)
    except Exception as e:
        logger.error(f"Error listing videos: {e}")
        return jsonify({"error": "Failed to list videos"}), 500

@app.route('/videos/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files:
        logger.error("No file part in request.")
        return jsonify({"error": "No file part"}), 400

    file = request.files['video']
    if file.filename == '':
        logger.error("No selected file.")
        return jsonify({"error": "No selected file"}), 400

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        logger.info(f"File uploaded successfully: {file.filename}")
        return jsonify({"message": "File uploaded"}), 200
    except Exception as e:
        logger.error(f"Failed to save file: {e}")
        return jsonify({"error": "Failed to upload file"}), 500

@app.route('/videos/<filename>', methods=['GET'])
def get_video(filename):
    try:
        logger.info(f"Serving video: {filename}")
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        logger.error(f"Video not found: {filename}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Failed to serve video: {e}")
        return jsonify({"error": "Failed to serve video"}), 500

@app.route('/videos/<filename>', methods=['DELETE'])
def delete_video(filename):
    try:
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        logger.info(f"File deleted: {filename}")
        return jsonify({"message": "File deleted"}), 200
    except FileNotFoundError:
        logger.error(f"File not found for deletion: {filename}")
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        return jsonify({"error": "Failed to delete file"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
