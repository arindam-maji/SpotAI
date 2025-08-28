"""
Configuration file for the Real-Time Object Detection App
"""

import os
from typing import Dict, Any

# Model Configuration
MODEL_CONFIG = {
    'default_model': 'yolov8n.pt',
    'available_models': [
        'yolov8n.pt',    # Nano - fastest, least accurate
        'yolov8s.pt',    # Small - good balance
        'yolov8m.pt',    # Medium - better accuracy
        'yolov8l.pt',    # Large - high accuracy
        'yolov8x.pt',    # Extra Large - highest accuracy, slowest
    ],
    'confidence_threshold': 0.5,
    'iou_threshold': 0.45,
    'max_detections': 300,
}

# Camera Configuration
CAMERA_CONFIG = {
    'default_resolution': (640, 480),
    'max_fps': 30,
    'buffer_size': 1,
    'timeout': 5000,  # milliseconds
    'retry_attempts': 3,
    'retry_delay': 1,  # seconds
}

# Network Configuration
NETWORK_CONFIG = {
    'droidcam_ports': [4747, 4748, 5050],
    'ip_webcam_ports': [8080, 8081],
    'connection_timeout': 5,  # seconds
    'scan_timeout': 1,  # seconds for network scanning
    'default_protocol': 'http',
}

# UI Configuration
UI_CONFIG = {
    'page_title': 'Real-Time Object Detection',
    'page_icon': '🎯',
    'layout': 'wide',
    'sidebar_width': 300,
    'video_width': 640,
    'show_fps': True,
    'show_detection_info': True,
    'refresh_rate': 0.033,  # ~30 FPS
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'use_threading': True,
    'frame_queue_size': 5,
    'processing_threads': 1,
    'memory_limit_mb': 512,
    'gpu_enabled': False,  # Set to True if GPU available
    'optimize_for_cpu': True,
}
