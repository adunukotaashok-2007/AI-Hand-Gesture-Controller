"""
Web-Based Gesture Simulator for GitHub Codespaces
Works in any browser environment without crashing on MediaPipe or Camera issues.
"""

from flask import Flask, Response, render_template_string, request, jsonify
import cv2
import numpy as np
import time

app = Flask(__name__)

# Try to import MediaPipe gracefully
MEDIAPIPE_AVAILABLE = False
try:
    import mediapipe as mp
    try:
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        MEDIAPIPE_AVAILABLE = True
    except AttributeError:
        from mediapipe.python.solutions import hands as mp_hands
        from mediapipe.python.solutions import drawing_utils as mp_draw
        MEDIAPIPE_AVAILABLE = True
except Exception:
    MEDIAPIPE_AVAILABLE = False

current_state = {
    "gesture": "No Hand",
    "action": "Waiting for input...",
    "status": "Ready",
    "last_update": time.time()
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Hand Gesture Controller - Demo</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Arial, sans-serif; }
        body { background: #121212; color: #f0f0f0; text-align: center; padding: 30px 15px; }
        h1 { color: #00E676; font-size: 28px; margin-bottom: 8px; }
        p.subtitle { color: #888; font-size: 14px; margin-bottom: 25px; }
        .container { max-width: 800px; margin: 0 auto; }
        .card { background: #1E1E1E; border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); border: 1px solid #333; margin-bottom: 25px; }
        .feed { width: 100%; max-width: 640px; border-radius: 8px; border: 2px solid #333; }
        .status-box { display: flex; justify-content: space-around; margin: 15px 0; }
        .status-item { background: #2A2A2A; padding: 12px 20px; border-radius: 8px; min-width: 140px; }
        .status-item span { display: block; font-size: 12px; color: #aaa; text-transform: uppercase; }
        .status-item strong { font-size: 18px; color: #00E676; }
        .btn-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 10px; margin-top: 15px; }
        button { background: #2D3748; color: white; border: 1px solid #4A5568; padding: 12px 8px; border-radius: 8px; font-size: 14px; cursor: pointer; transition: all 0.2s; }
        button:hover { background: #00E676; color: #000; font-weight: bold; border-color: #00E676; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 12px; background: #333; color: #888; margin-top: 10px; }
        .badge.active { background: #1B5E20; color: #81C784; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Hand Gesture Controller</h1>
        <p class="subtitle">Cloud Simulator & Visual Dashboard</p>

        <div class="card">
            <img src="/video_feed" class="feed" />

            <div class="status-box">
                <div class="status-item">
                    <span>Recognized Gesture</span>
                    <strong id="gesture-text">Loading...</strong>
                </div>
                <div class="status-item">
                    <span>Triggered Action</span>
                    <strong id="action-text" style="color:#FFD600;">Loading...</strong>
                </div>
            </div>

            <div class="badge {{ 'active' if mediapipe_ok else '' }}">
                {{ "✓ MediaPipe Engine Loaded" if mediapipe_ok else "⚡ Simulator Mode (Codespaces Cloud)" }}
            </div>
        </div>

        <div class="card">
            <h3 style="margin-bottom: 10px; color: #ccc;">Interactive Gesture Simulator</h3>
            <p style="font-size: 13px; color: #777; margin-bottom: 15px;">Click any gesture to simulate real-time detection:</p>
            <div class="btn-grid">
                <button onclick="triggerGesture('Thumbs Up', 'Volume Up (+10%)')">👍 Thumbs Up</button>
                <button onclick="triggerGesture('Thumbs Down', 'Volume Down (-10%)')">👎 Thumbs Down</button>
                <button onclick="triggerGesture('Open Palm', 'Play / Pause Media')">✋ Open Palm</button>
                <button onclick="triggerGesture('Two Fingers', 'Next Track / Slide')">✌️ Two Fingers</button>
                <button onclick="triggerGesture('Fist', 'Stop / Previous')">✊ Fist</button>
            </div>
        </div>
    </div>

    <script>
        function triggerGesture(gesture, action) {
            fetch('/simulate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({gesture: gesture, action: action})
            }).then(() => updateStatus());
        }

        function updateStatus() {
            fetch('/get_status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('gesture-text').innerText = data.gesture;
                    document.getElementById('action-text').innerText = data.action;
                });
        }
        setInterval(updateStatus, 1000);
        updateStatus();
    </script>
</body>
</html>
"""

def generate_frames():
    while True:
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Background design
        cv2.rectangle(frame, (0, 0), (640, 480), (25, 25, 25), -1)
        cv2.rectangle(frame, (10, 10), (630, 470), (45, 45, 45), 2)

        # Header Box
        cv2.rectangle(frame, (30, 30), (610, 120), (35, 35, 35), -1)
        cv2.putText(frame, "AI HAND GESTURE CONTROLLER", (50, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 230, 118), 2)
        cv2.putText(frame, "Status: SYSTEM ONLINE (CLOUD PREVIEW)", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180, 180, 180), 1)

        # Display Current Gesture
        cv2.rectangle(frame, (30, 150), (610, 350), (32, 32, 32), -1)
        cv2.putText(frame, "ACTIVE DETECTION", (50, 190),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)

        cv2.putText(frame, f"Gesture: {current_state['gesture']}", (50, 245),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(frame, f"Action : {current_state['action']}", (50, 295),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 214, 255), 2)

        # Footer Instruction
        cv2.putText(frame, "Click the gesture buttons below to test actions", (60, 410),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 200, 100), 1)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.05)

@app.route('/')
def index():
    return render_template_string(HTML_PAGE, mediapipe_ok=MEDIAPIPE_AVAILABLE)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/simulate', methods=['POST'])
def simulate():
    data = request.get_json()
    current_state["gesture"] = data.get("gesture", "Unknown")
    current_state["action"] = data.get("action", "None")
    current_state["last_update"] = time.time()
    return jsonify(success=True)

@app.route('/get_status')
def get_status():
    return jsonify(current_state)

if __name__ == '__main__':
    print("\n* Web Preview Server Starting on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)
