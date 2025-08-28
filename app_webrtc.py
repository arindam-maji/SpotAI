import streamlit as st
try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    import av
    WEBRTC_AVAILABLE = True
except ImportError:
    WEBRTC_AVAILABLE = False
    st.error("streamlit-webrtc not installed. Install with: pip install streamlit-webrtc")

import cv2
import numpy as np
from detector_improved import ObjectDetector
import threading
import queue

# Configure Streamlit page
st.set_page_config(
    page_title="WebRTC Object Detection",
    page_icon="🌐",
    layout="wide"
)

if not WEBRTC_AVAILABLE:
    st.stop()

# WebRTC configuration for better connectivity
RTC_CONFIGURATION = RTCConfiguration({
    "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
})

# Global variables for thread-safe communication
detection_result_queue = queue.Queue()
detector_instance = None

def get_detector():
    """Get or create detector instance"""
    global detector_instance
    if detector_instance is None:
        detector_instance = ObjectDetector(confidence=0.5)
    return detector_instance

class VideoProcessor:
    """Video frame processor for WebRTC"""

    def __init__(self):
        self.confidence = 0.5
        self.show_boxes = True
        self.detector = get_detector()

    def recv(self, frame):
        """Process incoming video frame"""
        try:
            # Convert frame to numpy array
            img = frame.to_ndarray(format="bgr24")

            if self.show_boxes:
                # Perform object detection
                annotated_frame, detections, summary = self.detector.detect_objects_detailed(
                    img, self.confidence
                )

                # Put detection results in queue for display
                try:
                    detection_result_queue.put_nowait({
                        'detections': detections,
                        'summary': summary
                    })
                except queue.Full:
                    pass  # Skip if queue is full

                return av.VideoFrame.from_ndarray(annotated_frame, format="bgr24")
            else:
                # Return original frame without detection
                return av.VideoFrame.from_ndarray(img, format="bgr24")

        except Exception as e:
            st.error(f"Error processing frame: {e}")
            # Return original frame on error
            img = frame.to_ndarray(format="bgr24")
            return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    st.title("🌐 WebRTC Real-Time Object Detection")
    st.markdown("**Browser-based real-time object detection using your webcam**")

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ Detection Settings")

        confidence_threshold = st.slider(
            "Confidence Threshold", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.5,
            step=0.05,
            key="confidence"
        )

        show_detections = st.checkbox("Enable Object Detection", value=True, key="show_boxes")

        show_stats = st.checkbox("Show Detection Statistics", value=True)

        st.markdown("---")
        st.header("📊 Model Information")

        # Display model info
        try:
            detector = get_detector()
            st.info(f"**Model:** YOLOv8 Nano\n**Classes:** {len(detector.class_names)}\n**Device:** {detector.device}")

        except Exception as e:
            st.error(f"Error loading model info: {e}")

        st.markdown("---")
        st.header("ℹ️ Instructions")

        st.markdown("""
        1. Click **START** to begin webcam streaming
        2. Allow camera access when prompted
        3. Adjust confidence threshold as needed
        4. Objects will be detected and highlighted in real-time

        **Note:** This uses WebRTC technology for browser-based streaming.
        """)

    # Main content area
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📹 Live Webcam Feed")

        # Create video processor with current settings
        video_processor = VideoProcessor()
        video_processor.confidence = confidence_threshold
        video_processor.show_boxes = show_detections

        # WebRTC streamer
        webrtc_ctx = webrtc_streamer(
            key="object-detection",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=RTC_CONFIGURATION,
            video_processor_factory=lambda: video_processor,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )

        # Camera status
        if webrtc_ctx.state.playing:
            st.success("🟢 Camera is active")
        else:
            st.info("📷 Click START to activate camera")

    with col2:
        st.subheader("🎯 Detection Results")

        if show_stats and webrtc_ctx.state.playing:
            # Display detection results
            detection_placeholder = st.empty()

            # Check for new detection results
            try:
                while not detection_result_queue.empty():
                    result = detection_result_queue.get_nowait()

                    with detection_placeholder.container():
                        summary = result['summary']
                        detections = result['detections']

                        # Display summary stats
                        if summary['total_objects'] > 0:
                            st.metric("Objects Detected", summary['total_objects'])
                            if 'avg_confidence' in summary:
                                st.metric("Avg Confidence", f"{summary['avg_confidence']:.2f}")

                            # Display detected classes
                            if summary['classes']:
                                st.markdown("**Detected Objects:**")
                                for class_name, count in summary['classes'].items():
                                    st.markdown(f"• {class_name}: {count}")
                        else:
                            st.info("No objects detected")

            except queue.Empty:
                pass

if __name__ == "__main__":
    main()
