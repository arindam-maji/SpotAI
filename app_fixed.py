import cv2
import streamlit as st
import threading
import time
import queue
from detector_improved import detect_objects

st.title("DroidCam / IP Webcam Object Detection")

# Input URL from the user
ip_url = st.text_input("Enter DroidCam / IP Webcam URL:", "http://192.168.18.44:4747/video")

# Control buttons
col1, col2 = st.columns(2)
with col1:
    start_button = st.button("🚀 Start Detection")
with col2:
    stop_button = st.button("⏹️ Stop Detection")

# Initialize session state
if 'camera_running' not in st.session_state:
    st.session_state.camera_running = False

def camera_worker(url, frame_queue, stop_event):
    """Background camera processing"""
    cap = cv2.VideoCapture(url)

    if not cap.isOpened():
        return

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects
        annotated_frame = detect_objects(frame)

        # Convert BGR to RGB
        annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

        # Add to queue
        if not frame_queue.full():
            frame_queue.put(annotated_frame)

        time.sleep(0.033)  # ~30 FPS

    cap.release()

# Handle buttons
if start_button:
    st.session_state.camera_running = True

if stop_button:
    st.session_state.camera_running = False

# Main camera loop
if ip_url and st.session_state.camera_running:

    # Test connection first
    cap_test = cv2.VideoCapture(ip_url)
    if not cap_test.isOpened():
        st.error("Cannot open video stream. Check your URL or Wi-Fi connection.")
        cap_test.release()
    else:
        cap_test.release()

        # Create frame queue and worker thread
        frame_queue = queue.Queue(maxsize=5)
        stop_event = threading.Event()

        # Start camera worker
        worker = threading.Thread(target=camera_worker, args=(ip_url, frame_queue, stop_event))
        worker.daemon = True
        worker.start()

        # Display frames
        stframe = st.empty()

        try:
            while st.session_state.camera_running:
                try:
                    frame = frame_queue.get(timeout=1.0)
                    stframe.image(frame, channels="RGB", use_column_width=True)
                except queue.Empty:
                    st.warning("Waiting for camera frames...")
                    continue

                time.sleep(0.01)
        except Exception as e:
            st.error(f"Error: {e}")
        finally:
            stop_event.set()
            st.session_state.camera_running = False

elif st.session_state.camera_running:
    st.warning("Please enter a camera URL")
