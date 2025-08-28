#!/usr/bin/env python3
"""
Launcher script for the Real-Time Object Detection App
"""

import sys
import subprocess
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import cv2
        import ultralytics
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    requirements_files = [
        'requirements_basic.txt',
        'requirements_cloud.txt',
        'requirements.txt'
    ]

    # Find available requirements file
    req_file = None
    for file in requirements_files:
        if os.path.exists(file):
            req_file = file
            break

    if req_file:
        print(f"Installing dependencies from {req_file}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
        return True
    else:
        print("No requirements file found!")
        return False

def main():
    """Main launcher function"""
    print("🎯 Real-Time Object Detection App Launcher")
    print("=" * 50)

    # Check for dependencies
    if not check_dependencies():
        print("\n📦 Installing dependencies...")
        if not install_dependencies():
            print("❌ Failed to install dependencies!")
            return

    print("✅ Dependencies are ready!")

    # Choose app version
    print("\n🚀 Choose app version:")
    print("1. Enhanced App (app_improved.py) - Recommended for local use")
    print("2. WebRTC Version (app_webrtc.py) - Better for remote deployment") 
    print("3. Fixed Original (app_fixed.py) - Your original code with fixes")

    choice = input("\nEnter choice (1-3): ").strip()

    app_files = {
        '1': 'app_improved.py',
        '2': 'app_webrtc.py', 
        '3': 'app_fixed.py'
    }

    app_file = app_files.get(choice)

    if not app_file:
        print("❌ Invalid choice!")
        return

    if not os.path.exists(app_file):
        print(f"❌ {app_file} not found!")
        return

    print(f"\n🚀 Launching {app_file}...")
    print("🌐 App will open in your browser automatically")
    print("Press Ctrl+C to stop the app\n")

    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', app_file,
            '--server.headless', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped!")

if __name__ == "__main__":
    main()
