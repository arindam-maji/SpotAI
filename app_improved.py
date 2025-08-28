import cv2
import streamlit as st
import numpy as np
import threading
import time
from detector_improved import detect_objects_detailed
from utils_improved import get_local_ip, test_camera_connection, get_camera_preset_urls
import queue

# Configure Streamlit page
st.set_page_config(
    page_title="Real-Time Object Detection",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state
if 'stop_camera' not in st.session_state:
    st.session_state.stop_camera = False
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False

def camera_stream(ip_url, frame_queue, stop_event):
    """Background thread function to handle camera streaming"""
    cap = None
    try:
        cap = cv2.VideoCapture(ip_url)

        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 15)  # Limit FPS for better performance

        if not cap.isOpened():
            return

        while not stop_event.is_set():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect objects
            try:
                annotated_frame, detections, summary = detect_objects_detailed(frame, confidence=0.5)
                # Convert BGR to RGB for Streamlit
                annotated_frame = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

                # Add frame to queue (non-blocking)
                if not frame_queue.full():
                    frame_queue.put({
                        'frame': annotated_frame,
                        'detections': detections,
                        'summary': summary
                    })

            except Exception as e:
                # If detection fails, just show original frame
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if not frame_queue.full():
                    frame_queue.put({
                        'frame': frame_rgb,
                        'detections': [],
                        'summary': {'total_objects': 0, 'classes': {}}
                    })

            # Small delay to prevent overwhelming
            time.sleep(0.033)  # ~30 FPS max

    except Exception as e:
        st.error(f"Error in camera stream: {e}")
    finally:
        if cap is not None:
            cap.release()

def main():
    st.title("🎯 Real-Time Object Detection")
    st.markdown("**Use your mobile as a webcam with DroidCam for real-time object detection**")

    # Sidebar for configuration
    with st.sidebar:
        st.header("📱 Camera Configuration")

        # Get local IP and generate camera URLs
        local_ip = get_local_ip()
        preset_urls = get_camera_preset_urls(local_ip.replace(local_ip.split('.')[-1], '100'))

        st.markdown("**Common DroidCam URL patterns:**")
        for name, url in preset_urls.items():
            st.code(url)

        ip_url = st.text_input(
            "Enter DroidCam/IP Webcam URL:", 
            value="http://192.168.18.44:4747/video",
            help="Make sure your phone and computer are on the same WiFi network"
        )

        st.markdown("---")
        st.header("🔧 Detection Settings")

        # Detection confidence threshold
        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.5,
            step=0.05
        )

        # Show detection info
        show_info = st.checkbox("Show Detection Info", value=True)

        st.markdown("---")
        st.header("📊 Connection Status")

        # Display local IP for reference
        st.info(f"Your computer's IP: {local_ip}")

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📹 Live Video Feed")

        # Control buttons
        button_col1, button_col2, button_col3 = st.columns(3)

        with button_col1:
            start_button = st.button("🚀 Start Camera", type="primary")
        with button_col2:
            stop_button = st.button("⏹️ Stop Camera")
        with button_col3:
            test_connection = st.button("🔍 Test Connection")

        # Video display placeholder
        video_placeholder = st.empty()

        # Status placeholder
        status_placeholder = st.empty()

    with col2:
        st.subheader("ℹ️ Information")
        info_placeholder = st.empty()

        # Instructions
        with st.expander("📖 How to Use", expanded=True):
            st.markdown("""
            **Setup Instructions:**
            1. Install DroidCam app on your phone
            2. Connect phone and computer to same WiFi
            3. Open DroidCam app and note the IP address
            4. Enter the URL in the format: `http://IP:4747/video`
            5. Click 'Start Camera' to begin detection

            **Troubleshooting:**
            - Ensure both devices are on same network
            - Try different ports: 4747, 4848, 5050
            - Restart DroidCam app if connection fails
            - Check firewall settings
            """)

        with st.expander("🎯 Detected Objects"):
            objects_placeholder = st.empty()

    # Handle button clicks
    if start_button and not st.session_state.camera_active:
        if ip_url:
            st.session_state.camera_active = True
            st.session_state.stop_camera = False
            status_placeholder.success("🟢 Starting camera...")
        else:
            st.warning("Please enter a valid camera URL")

    if stop_button and st.session_state.camera_active:
        st.session_state.stop_camera = True
        st.session_state.camera_active = False
        status_placeholder.info("🟡 Stopping camera...")
        video_placeholder.empty()

    if test_connection:
        with st.spinner("Testing connection..."):
            success, message = test_camera_connection(ip_url)
            if success:
                status_placeholder.success(f"✅ {message}")
            else:
                status_placeholder.error(f"❌ {message}")

    # Main camera loop
    if st.session_state.camera_active and not st.session_state.stop_camera:
        frame_queue = queue.Queue(maxsize=5)
        stop_event = threading.Event()

        # Start camera thread
        camera_thread = threading.Thread(
            target=camera_stream, 
            args=(ip_url, frame_queue, stop_event)
        )
        camera_thread.daemon = True
        camera_thread.start()

        # Display frames
        fps_counter = 0
        start_time = time.time()

        try:
            while st.session_state.camera_active and not st.session_state.stop_camera:
                try:
                    # Get frame from queue (with timeout)
                    result = frame_queue.get(timeout=1.0)
                    frame = result['frame']
                    detections = result['detections']
                    summary = result['summary']

                    # Display frame
                    video_placeholder.image(frame, channels="RGB", use_column_width=True)

                    # Update FPS counter
                    fps_counter += 1
                    elapsed_time = time.time() - start_time
                    if elapsed_time > 1:
                        fps = fps_counter / elapsed_time
                        status_placeholder.success(f"🟢 Live - FPS: {fps:.1f}")
                        fps_counter = 0
                        start_time = time.time()

                    # Update detection info
                    if show_info and summary['total_objects'] > 0:
                        info_text = f"""
                        **Detected Objects:** {summary['total_objects']}  
                        **Average Confidence:** {summary.get('avg_confidence', 0):.2f}  
                        **Classes Found:**
                        """
                        for class_name, count in summary['classes'].items():
                            info_text += f"\n• {class_name}: {count}"

                        objects_placeholder.markdown(info_text)
                    elif show_info:
                        objects_placeholder.info("No objects detected")

                    # Small delay to prevent UI overwhelming
                    time.sleep(0.01)

                except queue.Empty:
                    status_placeholder.warning("🟡 Waiting for frames...")
                    continue
                except Exception as e:
                    status_placeholder.error(f"❌ Display error: {e}")
                    break

        except KeyboardInterrupt:
            pass
        finally:
            stop_event.set()
            st.session_state.camera_active = False
            if camera_thread.is_alive():
                camera_thread.join(timeout=2)

if __name__ == "__main__":
    main()
