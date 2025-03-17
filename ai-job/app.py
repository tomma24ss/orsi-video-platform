import os
import subprocess
from ultralytics import YOLO
import cv2
import json
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
VIDEO_FILENAME = os.getenv("VIDEO_FILENAME")
INPUT_FOLDER = "/data/videos/uploaded"
PROCESSED_FOLDER = "/data/videos/processed"
METADATA_FOLDER = "/data/videos/metadata"
TEMP_FOLDER = "/data/videos/temp"
STATUS_FOLDER = "/data/videos/status"

# Ensure directories exist
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(METADATA_FOLDER, exist_ok=True)
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(STATUS_FOLDER, exist_ok=True)

def update_status(status, progress):
    """Write status to a file."""
    status_path = os.path.join(STATUS_FOLDER, f"{VIDEO_FILENAME}.json")
    with open(status_path, "w") as f:
        json.dump({"status": status, "progress": progress}, f)

def validate_video(file_path):
    """Validate video file using ffprobe."""
    try:
        result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries',
                                 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1',
                                 file_path], capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Video validation failed: {e}")
        return False

def reencode_video_to_h264(input_path, output_path):
    """Re-encode video using FFmpeg with H264 codec."""
    try:
        subprocess.run([
            'ffmpeg',
            '-y',
            '-i', input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '22',
            '-c:a', 'aac',
            '-b:a', '128k',
            output_path
        ], check=True)
        logger.info(f"Video successfully re-encoded to H264: {output_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to re-encode video to H264: {e}")

def process_video(filename):
    input_video_path = os.path.join(INPUT_FOLDER, filename)
    temp_video_path = os.path.join(TEMP_FOLDER, f"temp_{filename}")
    processed_video_path = os.path.join(PROCESSED_FOLDER, filename)
    metadata_path = os.path.join(METADATA_FOLDER, f"{filename}.json")

    if not os.path.exists(input_video_path):
        logger.error(f"Video not found: {input_video_path}")
        update_status("failed", 0)
        return

    # Load YOLO model
    model = YOLO("yolov8n.pt")
    logger.info("Loaded YOLO model.")

    # Open the video
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {input_video_path}")
        update_status("failed", 0)
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Video properties - Width: {width}, Height: {height}, FPS: {fps}, Total Frames: {total_frames}")

    # Start processing
    update_status("processing", 1)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video_path, fourcc, fps, (width, height))

    if not out.isOpened():
        logger.error(f"Failed to open VideoWriter for path: {temp_video_path}")
        cap.release()
        update_status("failed", 0)
        return

    metadata = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Run YOLO detection
        results = model(frame)

        frame_metadata = []
        for box, cls in zip(results[0].boxes.xyxy, results[0].boxes.cls):
            x1, y1, x2, y2 = map(int, box[:4])
            class_id = int(cls)
            label = results[0].names[class_id] if class_id in results[0].names else "unknown"

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            frame_metadata.append({
                "label": label,
                "bounding_box": [x1, y1, x2, y2]
            })

        metadata.append(frame_metadata)
        out.write(frame)
        frame_count += 1

        # Update progress accurately
        progress = max(1, int((frame_count / total_frames) * 100))
        update_status("processing", progress)

    cap.release()
    out.release()

    # Re-encode the processed video to H264
    reencode_video_to_h264(temp_video_path, processed_video_path)

    # Validate the final video
    if os.path.exists(processed_video_path) and validate_video(processed_video_path):
        logger.info(f"Processed video saved successfully: {processed_video_path}")
        update_status("completed", 100)
    else:
        logger.error(f"Processed video is invalid or not found: {processed_video_path}")
        update_status("failed", 0)

    os.remove(temp_video_path)  # Clean up temporary file

    # Save metadata
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    logger.info(f"Metadata saved: {metadata_path}")
    logger.info(f"Total frames processed: {frame_count}")

if __name__ == "__main__":
    if VIDEO_FILENAME:
        logger.info(f"Starting processing for: {VIDEO_FILENAME}")
        process_video(VIDEO_FILENAME)
    else:
        logger.error("No video filename specified in the environment variables.")
