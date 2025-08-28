import torch
import cv2
import numpy as np
from ultralytics import YOLO
from ultralytics.nn.tasks import DetectionModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Allowlist DetectionModel to fix unpickling errors
torch.serialization.add_safe_globals([DetectionModel])

class ObjectDetector:
    def __init__(self, model_path="yolov8n.pt", confidence=0.5, device="cpu"):
        """
        Initialize the object detector

        Args:
            model_path (str): Path to YOLO model weights
            confidence (float): Confidence threshold for detections
            device (str): Device to run inference on ('cpu' or 'cuda')
        """
        self.model_path = model_path
        self.confidence = confidence
        self.device = device
        self.model = None
        self.class_names = None

        self._load_model()

    def _load_model(self):
        """Load the YOLO model"""
        try:
            logger.info(f"Loading YOLO model: {self.model_path}")
            self.model = YOLO(self.model_path)

            # Set model to evaluation mode and move to device
            if self.device == "cuda" and torch.cuda.is_available():
                self.model.to("cuda")
                logger.info("Model loaded on GPU")
            else:
                self.model.to("cpu")
                logger.info("Model loaded on CPU")

            # Get class names
            self.class_names = self.model.names
            logger.info(f"Model loaded successfully with {len(self.class_names)} classes")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise

    def detect_objects_detailed(self, frame, conf_threshold=None):
        """
        Detect objects in a frame with detailed results

        Args:
            frame (numpy.ndarray): Input image frame
            conf_threshold (float): Override confidence threshold

        Returns:
            tuple: (annotated_frame, detections_list, summary_dict)
        """
        if self.model is None:
            logger.error("Model not loaded")
            return frame, [], {"total_objects": 0, "classes": {}}

        try:
            # Use provided threshold or default
            conf = conf_threshold if conf_threshold is not None else self.confidence

            # Run inference
            results = self.model(frame, conf=conf, verbose=False)

            # Get detection results
            detections = []
            if results and len(results) > 0:
                result = results[0]

                # Extract detection information
                if result.boxes is not None:
                    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding boxes
                    confidences = result.boxes.conf.cpu().numpy()  # Confidence scores
                    class_ids = result.boxes.cls.cpu().numpy().astype(int)  # Class IDs

                    for i, (box, confidence, class_id) in enumerate(zip(boxes, confidences, class_ids)):
                        x1, y1, x2, y2 = box
                        class_name = self.class_names.get(class_id, f"Class_{class_id}")

                        detections.append({
                            'box': [int(x1), int(y1), int(x2), int(y2)],
                            'confidence': float(confidence),
                            'class_id': int(class_id),
                            'class_name': class_name
                        })

                # Plot annotations on frame
                annotated_frame = result.plot()

                # Create summary
                summary = self.get_detection_summary(detections)

                return annotated_frame, detections, summary
            else:
                return frame, [], {"total_objects": 0, "classes": {}}

        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return frame, [], {"total_objects": 0, "classes": {}}

    def get_detection_summary(self, detections):
        """
        Get a summary of detections

        Args:
            detections (list): List of detection dictionaries

        Returns:
            dict: Summary statistics
        """
        if not detections:
            return {"total_objects": 0, "classes": {}}

        class_counts = {}
        for detection in detections:
            class_name = detection['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        return {
            "total_objects": len(detections),
            "classes": class_counts,
            "avg_confidence": np.mean([d['confidence'] for d in detections])
        }

# Global detector instance
_detector = None

def get_detector(model_path="yolov8n.pt", confidence=0.5):
    """Get or create detector instance"""
    global _detector
    if _detector is None:
        _detector = ObjectDetector(model_path, confidence)
    return _detector

def detect_objects(frame, confidence=0.5):
    """
    Simple function for backward compatibility

    Args:
        frame (numpy.ndarray): Input image frame
        confidence (float): Confidence threshold

    Returns:
        numpy.ndarray: Annotated frame
    """
    try:
        detector = get_detector(confidence=confidence)
        annotated_frame, _, _ = detector.detect_objects_detailed(frame, confidence)
        return annotated_frame
    except Exception as e:
        logger.error(f"Error in detect_objects: {e}")
        # Return original frame if detection fails
        return frame

def detect_objects_detailed(frame, confidence=0.5):
    """
    Detailed detection function returning both frame and detection info

    Args:
        frame (numpy.ndarray): Input image frame
        confidence (float): Confidence threshold

    Returns:
        tuple: (annotated_frame, detections_list, summary_dict)
    """
    try:
        detector = get_detector(confidence=confidence)
        return detector.detect_objects_detailed(frame, confidence)
    except Exception as e:
        logger.error(f"Error in detect_objects_detailed: {e}")
        return frame, [], {"total_objects": 0, "classes": {}}
