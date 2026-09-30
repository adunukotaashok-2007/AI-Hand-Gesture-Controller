"""
Web-Based Gesture Simulator for GitHub Codespaces
Opens a live web page inside Codespaces to test gesture logic without desktop GUI.
"""

from flask import Flask, Response, render_template_string
import cv2
import numpy as np
import mediapipe as mp

app = Flask(__name__)

# MediaPipe Setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)
mp_draw = mp.solutions.drawing_utils

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Gesture Controller - Web Preview</title>
    <style>
        body { background: #1a1a1a; color: white; font-family: Arial; text-align: center; padding: 20px; }
        .box { background: #2a2a2a; border-radius: 10px; display: inline-block; padding: 20px; margin-top: 10px; }
        h1 { color: #4CAF50; }
        p { font-size: 16px; color: #ccc; }
        .badge { background: #333; padding: 6px 12px; border-radius: 5px; margin: 4px; display: inline-block; }
    </style>
</head>
<body>
    <h1>🤖 AI Hand Gesture Controller</h1>
    <p>Web Demonstration Interface</p>
    <div class="box">
        <img src="/video_feed" width="640" height="480" style="border-radius:8px; border:2px solid #444;" />
        <br/><br/>
        <div>
            <span class="badge">👍 Thumbs Up = Vol+</span>
            <span class="badge">👎 Thumbs Down = Vol-</span>
            <span class="badge">✋ Open Palm = Play/Pause</span>
            <span class="badge">✌️ Two Fingers = Next</span>
            <span class="badge">✊ Fist = Prev</span>
        </div>
    </div>
</body>
</html>
"""

def generate_frames():
    # If in cloud with no camera, generate a demonstration canvas
    cap = cv2.VideoCapture(0)
    has_cam = cap.isOpened()

    angle = 0
    while True:
        if has_cam:
            success, frame = cap.read()
            if not success:
                continue
            frame = cv2.flip(frame, 1)
        else:
            # Create synthetic demo canvas when no webcam exists in cloud
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.rectangle(frame, (20, 20), (620, 460), (35, 35, 35), -1)
            cv2.putText(frame, "No Physical Camera in Codespaces", (70, 200),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 165, 255), 2)
            cv2.putText(frame, "Run on your Laptop for Live Webcam Mode", (60, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

            # Draw an animated status indicator
            angle = (angle + 5) % 360
            x = int(320 + 40 * np.cos(np.radians(angle)))
            y = int(340 + 40 * np.sin(np.radians(angle)))
            cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
            cv2.putText(frame, "System Active & Waiting", (220, 410),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 100), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("\n* Web Preview Server Running...")
    print("* Codespaces will show an 'Open in Browser' popup button at bottom-right.\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
