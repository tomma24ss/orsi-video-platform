from flask import current_app as app
import os
import re
from flask import send_from_directory
from utils.logger import logger
from exceptions.api_exceptions import APIException

class VideoService:

    @staticmethod
    def list_videos(folder: str) -> list:
        """List all videos in the specified folder."""
        try:
            return [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
        except Exception as e:
            raise Exception(f"Failed to list videos in {folder}: {e}")

    @staticmethod
    def save_video(file, folder: str) -> str:
        """Save video to the specified folder."""
        filename = file.filename
        save_path = os.path.join(folder, filename)
        file.save(save_path)
        return filename

    @staticmethod
    def get_video(filename):
        try:
            logger.info(f"Serving video: {filename}")
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename,  mimetype='video/mp4')
        except FileNotFoundError:
            logger.error(f"Video not found: {filename}")
            raise APIException("File not found", 404)

    @staticmethod
    def delete_video(filename: str, folder: str) -> None:
        """Delete the specified video from the folder."""
        file_path = os.path.join(folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise Exception(f"File {filename} not found in {folder}.")

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
