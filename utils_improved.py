"""
Utility functions for the object detection app
"""

import socket
import cv2
import requests
import logging
import time
from typing import List, Dict, Tuple, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip() -> str:
    """
    Returns the local LAN IP address (e.g. 192.168.x.x).
    Useful to open Streamlit app on other devices in same WiFi.

    Returns:
        str: Local IP address
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a remote server (doesn't need to be reachable)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip

def test_camera_connection(url: str, timeout: int = 5) -> Tuple[bool, str]:
    """
    Test if a camera URL is accessible

    Args:
        url (str): Camera URL to test
        timeout (int): Timeout in seconds

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        cap = cv2.VideoCapture(url)
        cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)  # Convert to milliseconds

        if not cap.isOpened():
            cap.release()
            return False, "Cannot open video stream"

        # Try to read a frame
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return False, "Cannot read frame from stream"

        return True, f"Connection successful - Frame size: {frame.shape[1]}x{frame.shape[0]}"

    except Exception as e:
        return False, f"Connection error: {str(e)}"

def get_droidcam_urls(base_ip: str) -> List[str]:
    """
    Generate common DroidCam URL patterns for a given IP

    Args:
        base_ip (str): Base IP address (e.g., "192.168.1.100")

    Returns:
        list: List of possible DroidCam URLs
    """
    ports = [4747, 4748, 5050, 8080]
    urls = []

    for port in ports:
        urls.extend([
            f"http://{base_ip}:{port}/video",
            f"http://{base_ip}:{port}/mjpeg.mjpg",
            f"http://{base_ip}:{port}/stream",
        ])

    return urls

def optimize_frame_for_detection(frame: np.ndarray, 
                                max_width: int = 640,
                                max_height: int = 480) -> np.ndarray:
    """
    Optimize frame size for better detection performance

    Args:
        frame (numpy.ndarray): Input frame
        max_width (int): Maximum width
        max_height (int): Maximum height

    Returns:
        numpy.ndarray: Resized frame
    """
    height, width = frame.shape[:2]

    # Calculate scaling factor
    scale_w = max_width / width
    scale_h = max_height / height
    scale = min(scale_w, scale_h, 1.0)  # Don't upscale

    if scale < 1.0:
        new_width = int(width * scale)
        new_height = int(height * scale)
        frame = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)

    return frame

# Camera configuration presets
CAMERA_PRESETS = {
    'droidcam_wifi': {
        'name': 'DroidCam WiFi',
        'url_pattern': 'http://{ip}:4747/video',
        'description': 'Standard DroidCam over WiFi'
    },
    'droidcam_alt': {
        'name': 'DroidCam Alternative Port',
        'url_pattern': 'http://{ip}:4748/video',
        'description': 'DroidCam with alternative port'
    },
    'ip_webcam': {
        'name': 'IP Webcam',
        'url_pattern': 'http://{ip}:8080/video',
        'description': 'IP Webcam app'
    }
}

def get_camera_preset_urls(ip: str) -> Dict[str, str]:
    """
    Get camera URLs for different presets

    Args:
        ip (str): IP address

    Returns:
        dict: Dictionary of preset names to URLs
    """
    urls = {}

    for preset_key, preset_info in CAMERA_PRESETS.items():
        urls[preset_info['name']] = preset_info['url_pattern'].format(ip=ip)

    return urls
