from flask import current_app as app
import os
import re
from flask import send_from_directory
from utils.logger import logger
from exceptions.api_exceptions import APIException

class VideoService:

    @staticmethod
    def list_videos():
        try:
            videos = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith('.mp4')]
            logger.info(f"Listing videos: {videos}")
            return videos
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            raise APIException("Failed to list videos", 500)

    @staticmethod
    def save_video(file):
        try:
            unique_filename = VideoService.get_unique_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            logger.info(f"File uploaded successfully: {unique_filename}")
            return unique_filename
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            raise APIException("Failed to upload file", 500)

    @staticmethod
    def get_video(filename):
        try:
            logger.info(f"Serving video: {filename}")
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        except FileNotFoundError:
            logger.error(f"Video not found: {filename}")
            raise APIException("File not found", 404)

    @staticmethod
    def delete_video(filename):
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            logger.info(f"File deleted: {filename}")
        except FileNotFoundError:
            logger.error(f"File not found for deletion: {filename}")
            raise APIException("File not found", 404)

    @staticmethod
    def get_unique_filename(filename):
        # Split the filename and extension
        base, extension = os.path.splitext(filename)

        # Sanitize the base name for Kubernetes compatibility
        sanitized_base = re.sub(r'[^a-z0-9.-]', '-', base.lower())
        sanitized_base = re.sub(r'^[^a-z0-9]+', '', sanitized_base)
        sanitized_base = re.sub(r'[^a-z0-9]+$', '', sanitized_base)

        # Start with the sanitized filename
        unique_filename = f"{sanitized_base}{extension}"
        counter = 1

        # Ensure uniqueness by adding a counter if needed
        while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)):
            unique_filename = f"{sanitized_base}-{counter}{extension}"
            counter += 1

        return unique_filename
