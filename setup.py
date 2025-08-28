#!/usr/bin/env python3
"""
Setup script for Real-Time Object Detection App
"""

import os
import sys
import subprocess

def create_directories():
    """Create necessary directories"""
    directories = ['models', 'temp', 'logs', 'output']

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def download_model():
    """Download YOLO model if not exists"""
    model_file = 'yolov8n.pt'

    if not os.path.exists(model_file):
        print("📥 Downloading YOLOv8 nano model...")
        try:
            import ultralytics
            from ultralytics import YOLO

            # This will automatically download the model
            model = YOLO(model_file)
            print("✅ Model downloaded successfully!")
        except Exception as e:
            print(f"❌ Error downloading model: {e}")

def check_system():
    """Check system requirements"""
    print("🔍 Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher required!")
        return False

    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

    return True

def main():
    """Main setup function"""
    print("🎯 Real-Time Object Detection App Setup")
    print("=" * 50)

    # Check system
    if not check_system():
        return

    # Create directories
    print("\n📁 Creating directories...")
    create_directories()

    # Download model
    print("\n🤖 Setting up AI model...")
    download_model()

    print("\n✅ Setup complete!")
    print("\n🚀 You can now run:")
    print("   python launcher.py")
    print("   or")
    print("   streamlit run app_improved.py")

if __name__ == "__main__":
    main()
