import os
from ultralytics import YOLO
import cv2
import json
import logging

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
VIDEO_FILENAME = os.getenv("VIDEO_FILENAME")
INPUT_FOLDER = "/data/videos"
METADATA_FOLDER = "/data/videos/metadata"

os.makedirs(METADATA_FOLDER, exist_ok=True)

def process_video(filename):
    video_path = os.path.join(INPUT_FOLDER, filename)
    metadata_path = os.path.join(METADATA_FOLDER, f"{filename}.json")

    if not os.path.exists(video_path):
        logger.error(f"Video not found: {video_path}")
        return

    # Load YOLO model
    model = YOLO("yolov8n.pt")
    logger.info(f"Loaded YOLO model.")

    # Open the video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    # Setup video writer (overwrite original)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))

    metadata = []

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

            # Draw bounding box and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            frame_metadata.append({
                "label": label,
                "bounding_box": [x1, y1, x2, y2]
            })

        metadata.append(frame_metadata)
        out.write(frame)

    cap.release()
    out.release()

    # Save metadata
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)

    logger.info(f"Processed and saved video: {video_path}")
    logger.info(f"Metadata saved: {metadata_path}")

if __name__ == "__main__":
    if VIDEO_FILENAME:
        logger.info(f"Starting processing for: {VIDEO_FILENAME}")
        process_video(VIDEO_FILENAME)
    else:
        logger.error("No video filename specified in the environment variables.")
