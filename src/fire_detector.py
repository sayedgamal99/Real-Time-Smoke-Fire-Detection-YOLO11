import cv2
import numpy as np
from ultralytics import YOLO
import cvzone
import logging
from pathlib import Path


class FireDetector:
    def __init__(self, model_path: Path, target_height: int = 500):
        """
        Initialize the FireDetector with a YOLO model.
        
        Args:
            model_path (Path): Path to the YOLO model file
            target_height (int): Target height for frame resizing
        """
        self.logger = logging.getLogger(__name__)

        try:
            self.model = YOLO(str(model_path))
            self.target_height = target_height
            self.names = self.model.model.names
            self.logger.info("Fire detector initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize fire detector: {e}")
            raise

    def resize_frame(self, frame):
        """Resize frame maintaining aspect ratio."""
        height, width = frame.shape[:2]
        aspect_ratio = width / height
        new_width = int(self.target_height * aspect_ratio)
        return cv2.resize(frame, (new_width, self.target_height))

    def process_frame(self, frame):
        """
        Process a video frame to detect fire.
        
        Returns:
            tuple: (processed_frame, fire_detected)
        """
        try:
            frame = self.resize_frame(frame)
            results = self.model(frame)
            fire_detected = False

            if len(results) > 0:
                boxes = results[0].boxes.xyxy.cpu(
                ).numpy().astype(int)  # Bounding boxes
                class_ids = results[0].boxes.cls.cpu(
                ).numpy().astype(int)  # Class IDs
                # Confidence scores
                confidences = results[0].boxes.conf.cpu().numpy()

                overlay = frame.copy()

                for box, class_id, confidence in zip(boxes, class_ids, confidences):
                    class_name = self.names[class_id]
                    x1, y1, x2, y2 = box

                    # Draw bounding box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cvzone.putTextRect(frame, f'{class_name}: {
                                       confidence:.2f}', (x1, y1), 1, 1)

                    # Check if fire is detected
                    if 'fire' in class_name.lower():
                        fire_detected = True

                # Optionally, you can add overlay blending for bounding boxes
                # frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

            return frame, fire_detected

        except Exception as e:
            self.logger.error(f"Error processing frame: {e}")
            return frame, False
