import queue
import threading
import time

import cv2
import numpy as np
import streamlit as st

from detector_improved import detect_objects_detailed
from utils_improved import (get_camera_preset_urls, get_local_ip,
                            test_camera_connection)

# ------------------- Streamlit page config -------------------
st.set_page_config(
    page_title="SpotAI - Real-Time Object Detection",
    page_icon="🎯",
    layout="wide"
)

# ------------------- Session State Initialization -------------------
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'stop_camera' not in st.session_state:
    st.session_state.stop_camera = False
if 'camera_thread' not in st.session_state:
    st.session_state.camera_thread = None
if 'frame_queue' not in st.session_state:
    st.session_state.frame_queue = queue.Queue(maxsize=5)
if 'stop_event' not in st.session_state:
    st.session_state.stop_event = threading.Event()

# ------------------- Camera Stream Thread -------------------
def camera_stream(ip_url, frame_queue, stop_event, confidence_threshold):
    """Capture frames from IP camera and perform object detection."""
    cap = None
    try:
        cap = cv2.VideoCapture(ip_url)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)

        if not cap.isOpened():
            st.error("Failed to open camera. Check URL or connection.")
            return

        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                continue

            try:
                annotated_frame, detections, summary = detect_objects_detailed(frame, confidence=confidence_threshold)
                annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
            except Exception:
                annotated_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                summary = {'total_objects': 0, 'classes': {}}

            if not frame_queue.full():
                frame_queue.put({'frame': annotated_frame, 'summary': summary})

            time.sleep(0.033)  # ~30 FPS
    finally:
        if cap:
            cap.release()

# ------------------- Main Function -------------------
def main():
    st.title("🎯 SpotAI - Real-Time Object Detection")
    st.markdown("Use your mobile as a webcam (DroidCam/IP Webcam) for real-time detection")

    # ------------------- Sidebar -------------------
    with st.sidebar:
        st.header("📱 Camera Configuration")
        local_ip = get_local_ip()
        preset_urls = get_camera_preset_urls(local_ip.replace(local_ip.split('.')[-1], '100'))
        st.markdown("**Common DroidCam URLs:**")
        for name, url in preset_urls.items():
            st.code(url)

        ip_url = st.text_input(
            "Enter Camera URL:",
            value="http://192.168.18.44:4747/video",
            help="Phone and computer must be on same WiFi"
        )

        st.markdown("---")
        st.header("🔧 Detection Settings")
        confidence_threshold = st.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.05)
        show_info = st.checkbox("Show Detection Info", value=True)

        st.markdown("---")
        st.header("📊 Connection Status")
        st.info(f"Your computer IP: {local_ip}")

    # ------------------- Main UI -------------------
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("📹 Live Video Feed")
        button_col1, button_col2, button_col3 = st.columns(3)
        with button_col1:
            start_button = st.button("🚀 Start Camera")
        with button_col2:
            stop_button = st.button("⏹️ Stop Camera")
        with button_col3:
            test_connection = st.button("🔍 Test Connection")

        video_placeholder = st.empty()
        status_placeholder = st.empty()

    with col2:
        st.subheader("ℹ️ Information")
        info_placeholder = st.empty()
        with st.expander("📖 How to Use", expanded=True):
            st.markdown("""
            1. Install DroidCam on your phone
            2. Connect phone and computer to same WiFi
            3. Open DroidCam and note the IP
            4. Enter URL: `http://IP:4747/video`
            5. Click 'Start Camera'
            """)
        objects_placeholder = st.empty()

    # ------------------- Button Actions -------------------
    if start_button and not st.session_state.camera_active:
        if ip_url:
            st.session_state.camera_active = True
            st.session_state.stop_camera = False
            st.session_state.stop_event.clear()
            if st.session_state.camera_thread is None or not st.session_state.camera_thread.is_alive():
                st.session_state.camera_thread = threading.Thread(
                    target=camera_stream,
                    args=(ip_url, st.session_state.frame_queue, st.session_state.stop_event, confidence_threshold)
                )
                st.session_state.camera_thread.daemon = True
                st.session_state.camera_thread.start()
            st.success("🟢 Camera started")
        else:
            st.warning("Enter a valid camera URL")

    if stop_button and st.session_state.camera_active:
        st.session_state.stop_camera = True
        st.session_state.camera_active = False
        st.session_state.stop_event.set()
        st.success("🟡 Camera stopped")

    if test_connection:
        with st.spinner("Testing camera connection..."):
            success, message = test_camera_connection(ip_url)
            if success:
                st.success(f"✅ {message}")
            else:
                st.error(f"❌ {message}")

    # ------------------- Display Loop -------------------
    fps_counter = 0
    start_time = time.time()
    while st.session_state.camera_active and not st.session_state.stop_camera:
        try:
            result = st.session_state.frame_queue.get(timeout=1.0)
            frame = result['frame']
            summary = result['summary']
            video_placeholder.image(frame, channels="RGB", use_column_width=True)

            # FPS
            fps_counter += 1
            elapsed = time.time() - start_time
            if elapsed > 1:
                fps = fps_counter / elapsed
                status_placeholder.success(f"🟢 Live - FPS: {fps:.1f}")
                fps_counter = 0
                start_time = time.time()

            # Detection info
            if show_info:
                if summary['total_objects'] > 0:
                    info_text = f"**Detected Objects:** {summary['total_objects']}\n"
                    for cls, count in summary['classes'].items():
                        info_text += f"• {cls}: {count}\n"
                    objects_placeholder.markdown(info_text)
                else:
                    objects_placeholder.info("No objects detected")

            time.sleep(0.01)
        except queue.Empty:
            status_placeholder.warning("🟡 Waiting for frames...")
        except Exception as e:
            status_placeholder.error(f"❌ Display error: {e}")
            break

    # Cleanup on stop
    st.session_state.stop_event.set()
    st.session_state.camera_active = False
    if st.session_state.camera_thread is not None:
        st.session_state.camera_thread.join(timeout=2)

# ------------------- Run App -------------------
if __name__ == "__main__":
    main()
