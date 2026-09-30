"""
Run this FIRST to find out exactly what's broken.
Command: python diagnose.py
"""

print("=" * 50)
print("  DIAGNOSTIC CHECK")
print("=" * 50)

# CHECK 1: Python version
import sys
print(f"\n[1] Python version: {sys.version}")
if sys.version_info < (3, 8):
    print("    ❌ FAIL: Need Python 3.8+")
else:
    print("    ✅ OK")

# CHECK 2: OpenCV
try:
    import cv2
    print(f"\n[2] OpenCV version: {cv2.__version__}")
    print("    ✅ OK")
except ImportError:
    print("\n[2] OpenCV")
    print("    ❌ FAIL: Run → pip install opencv-python")

# CHECK 3: MediaPipe
try:
    import mediapipe as mp
    print(f"\n[3] MediaPipe version: {mp.__version__}")
    print("    ✅ OK")
except ImportError:
    print("\n[3] MediaPipe")
    print("    ❌ FAIL: Run → pip install mediapipe")

# CHECK 4: PyAutoGUI
try:
    import pyautogui
    print(f"\n[4] PyAutoGUI: installed")
    print("    ✅ OK")
except ImportError:
    print("\n[4] PyAutoGUI")
    print("    ❌ FAIL: Run → pip install pyautogui")

# CHECK 5: Camera
try:
    import cv2
    print(f"\n[5] Testing camera...")
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"    ✅ OK - Camera works! Frame size: {frame.shape}")
        else:
            print("    ⚠️  Camera opened but can't read frames")
        cap.release()
    else:
        print("    ❌ FAIL: Camera index 0 not found")
        print("    → Try closing Zoom/Teams/other camera apps")
        print("    → Or change camera_index to 1 or 2 in camera.py")
except Exception as e:
    print(f"    ❌ FAIL: {e}")

# CHECK 6: src module import
print(f"\n[6] Testing src imports...")
try:
    from src.camera import Camera
    print("    ✅ src.camera OK")
except Exception as e:
    print(f"    ❌ src.camera FAIL: {e}")

try:
    from src.hand_detector import HandDetector
    print("    ✅ src.hand_detector OK")
except Exception as e:
    print(f"    ❌ src.hand_detector FAIL: {e}")

try:
    from src.gesture_recognizer import GestureRecognizer
    print("    ✅ src.gesture_recognizer OK")
except Exception as e:
    print(f"    ❌ src.gesture_recognizer FAIL: {e}")

try:
    from src.action_controller import ActionController
    print("    ✅ src.action_controller OK")
except Exception as e:
    print(f"    ❌ src.action_controller FAIL: {e}")

try:
    from src.gesture_logger import GestureLogger
    print("    ✅ src.gesture_logger OK")
except Exception as e:
    print(f"    ❌ src.gesture_logger FAIL: {e}")

try:
    from src.application import Application
    print("    ✅ src.application OK")
except Exception as e:
    print(f"    ❌ src.application FAIL: {e}")

print("\n" + "=" * 50)
print("  Run 'python main.py' from the SAME folder")
print("  that contains main.py and the src/ folder!")
print("=" * 50)
