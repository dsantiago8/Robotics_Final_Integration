# Face-Tracking Servo Controller

A real-time face-tracking system that uses Python, OpenCV, and MediaPipe to detect a user's face, control two servo motors (pan/tilt) via Arduino, and automatically capture a photo when the face is centered for a specified duration. Once captured, the system sends a trigger signal to a second Arduino for further actions (e.g., lights, countdown, animation, etc.).

---

## 🔧 Features

- 📷 Real-time face detection with MediaPipe
- 🧠 Smooth servo movement using serial commands
- 🎯 Auto-centering logic with deadzones and fine tuning
- 🖼️ Screenshot capture after 2+ seconds of centered alignment
- 🔁 Dual-Arduino support: one for servos, one for external trigger (COM6)
- 💾 Saves timestamped screenshots to a local folder

---

## 🛠️ Hardware Requirements

- Arduino Uno or Nano ×2 (or one with multiple tasks)
- 2x Servo motors (e.g., SG90)
- USB cables for serial connection
- Computer with Python 3.x and webcam

---

## 🐍 Software Stack

- Python 3
- OpenCV
- MediaPipe
- PySerial

---

## 📦 Installation

### 1. Clone this repository

```bash
git clone https://github.com/yourusername/Track-n-Snap.git
cd Track-n-Snap
