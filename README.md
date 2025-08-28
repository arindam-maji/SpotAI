# 🎯 Real-Time Object Detection App

A comprehensive real-time object detection application that uses your mobile phone as a webcam. Built with **Streamlit** and **YOLOv8** for fast, accurate object detection.

## ✨ Features

- 📱 **Mobile Camera Support**: Use DroidCam or IP Webcam to turn your phone into a webcam
- 🎯 **Real-Time Detection**: Live object detection with YOLOv8 models
- 🌐 **Multiple Interfaces**: Choose between OpenCV-based or WebRTC-based streaming
- ⚙️ **Configurable Settings**: Adjustable confidence thresholds and detection parameters
- 🚀 **Optimized Performance**: CPU-optimized for Streamlit Cloud deployment
- 📊 **Detection Analytics**: Real-time statistics and detection information
- 🔧 **Network Tools**: Built-in connection testing and troubleshooting

## 🚀 Quick Start

### Option 1: Enhanced App (Recommended for Local Use)

1. **Install Dependencies**
   ```bash
   pip install -r requirements_basic.txt
   ```

2. **Set Up DroidCam**
   - Download DroidCam app on your phone
   - Connect phone and computer to same WiFi network
   - Note the IP address shown in the app

3. **Run the App**
   ```bash
   streamlit run app_improved.py
   ```

### Option 2: WebRTC Version (Better for Remote Deployment)

1. **Install Dependencies**
   ```bash
   pip install -r requirements_webrtc.txt
   ```

2. **Run the WebRTC App**
   ```bash
   streamlit run app_webrtc.py
   ```

### Option 3: Easy Launcher

1. **Run the Setup**
   ```bash
   python setup.py
   ```

2. **Launch with Interactive Menu**
   ```bash
   python launcher.py
   ```

## 📁 Project Structure

```
real-time-object-detection/
├── app_improved.py          # Main enhanced app
├── app_webrtc.py            # WebRTC-based app
├── app_fixed.py             # Fixed version of original
├── detector_improved.py     # Enhanced object detection module
├── utils_improved.py        # Utility functions
├── config.py               # Configuration settings
├── requirements.txt        # Main requirements
├── requirements_basic.txt   # Dependencies for OpenCV version
├── requirements_webrtc.txt  # Dependencies for WebRTC version
├── requirements_cloud.txt   # Streamlit Cloud optimized dependencies
├── launcher.py             # Interactive launcher
├── setup.py                # Setup script
├── README.md               # This file
└── QUICK_START.md          # Quick start guide
```

## 🔧 Configuration

### Camera Setup

1. **DroidCam Setup**
   - Install DroidCam app from Play Store/App Store
   - Connect to same WiFi network as your computer
   - Start server in the app
   - Use URL format: `http://YOUR_PHONE_IP:4747/video`

2. **IP Webcam Setup**
   - Install IP Webcam app
   - Configure settings (resolution, quality, etc.)
   - Start server
   - Use URL format: `http://YOUR_PHONE_IP:8080/video`

### Model Configuration

The app supports multiple YOLO models:
- **YOLOv8n** (Nano): Fastest, lowest accuracy
- **YOLOv8s** (Small): Good balance of speed and accuracy
- **YOLOv8m** (Medium): Better accuracy, moderate speed
- **YOLOv8l** (Large): High accuracy, slower
- **YOLOv8x** (Extra Large): Highest accuracy, slowest

## 🌐 Deployment Options

### Local Development
```bash
# Clone and setup
git clone <repository>
cd real-time-object-detection
pip install -r requirements_basic.txt

# Run locally
streamlit run app_improved.py
```

### Streamlit Cloud Deployment

1. **Prepare for Deployment**
   - Use `requirements_cloud.txt` for dependencies
   - Ensure all files are in your GitHub repository
   - Use the WebRTC version (`app_webrtc.py`) for remote deployment

2. **Deploy to Streamlit Cloud**
   - Connect your GitHub repository to Streamlit Cloud
   - Select `app_webrtc.py` as the main file
   - Use `requirements_cloud.txt` as requirements file

## 🛠️ Troubleshooting

### Camera Connection Issues

**Problem**: Cannot connect to camera
- ✅ Ensure phone and computer are on same WiFi network
- ✅ Check if DroidCam server is running on phone
- ✅ Try different ports: 4747, 4748, 5050
- ✅ Disable firewall temporarily
- ✅ Restart router and devices

**Problem**: Poor video quality
- ✅ Improve lighting conditions
- ✅ Clean phone camera lens
- ✅ Reduce resolution in DroidCam settings
- ✅ Move closer to WiFi router

### Performance Issues

**Problem**: Low FPS or lag
- ✅ Close other applications
- ✅ Use YOLOv8n (nano) model for faster processing
- ✅ Reduce video resolution
- ✅ Lower confidence threshold

### Detection Issues

**Problem**: Objects not being detected
- ✅ Lower confidence threshold
- ✅ Ensure good lighting
- ✅ Objects should be clearly visible
- ✅ Try different YOLO model

## 📊 Performance Optimization

### For CPU Deployment (Streamlit Cloud)
- Use YOLOv8n model for best performance
- Keep confidence threshold around 0.5-0.6
- Limit frame rate to 15-20 FPS

### For Local GPU Deployment
- Can use larger models (YOLOv8s, YOLOv8m)
- Higher frame rates possible
- Better accuracy with larger models

## 🔐 Security Considerations

- **Network Security**: DroidCam streams are unencrypted HTTP
- **Local Network Only**: Don't expose camera feeds to public networks
- **Firewall**: Configure appropriate firewall rules
- **Privacy**: Be mindful of what's visible in camera feed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Ultralytics**: For the excellent YOLOv8 implementation
- **Streamlit**: For the amazing web app framework
- **OpenCV**: For computer vision capabilities
- **DroidCam**: For mobile camera streaming solution

---

Made with ❤️ for computer vision enthusiasts
