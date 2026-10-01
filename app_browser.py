cat << 'EOF' > app_browser.py
from flask import Flask, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>AI Hand Gesture Controller</title>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; flex-direction: column; align-items: center; min-height: 100vh; padding: 15px; }
        .header { text-align: center; margin-bottom: 12px; }
        .header h1 { font-size: 24px; color: #38bdf8; }
        
        .main-layout { display: flex; flex-wrap: wrap; gap: 15px; justify-content: center; max-width: 1000px; width: 100%; }
        
        /* Camera Box */
        .camera-card { position: relative; width: 520px; height: 390px; max-width: 95vw; background: #000; border-radius: 12px; overflow: hidden; border: 2px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        video { display: none; }
        canvas { width: 100%; height: 100%; transform: scaleX(-1); }
        
        /* Media Player Box */
        .player-card { flex: 1; min-width: 320px; max-width: 420px; background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; display: flex; flex-direction: column; justify-content: space-between; }
        
        .hud { position: absolute; top: 10px; left: 10px; right: 10px; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(4px); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; font-size: 13px; z-index: 10; }
        .hud strong { color: #4ade80; font-size: 15px; }
        .hud span { color: #38bdf8; font-weight: bold; }
        
        /* Media Player Elements */
        .track-info { text-align: center; margin-bottom: 15px; }
        .track-title { font-size: 18px; font-weight: bold; color: #f8fafc; }
        .track-status { font-size: 13px; color: #94a3b8; margin-top: 3px; }
        
        .vol-container { margin: 15px 0; }
        .vol-label { display: flex; justify-content: space-between; font-size: 13px; color: #cbd5e1; margin-bottom: 5px; }
        .vol-bar { width: 100%; height: 12px; background: #334155; border-radius: 6px; overflow: hidden; }
        .vol-fill { width: 70%; height: 100%; background: linear-gradient(90deg, #38bdf8, #4ade80); transition: width 0.2s; }
        
        .action-banner { background: #020617; border: 1px solid #38bdf8; border-radius: 8px; padding: 12px; text-align: center; margin: 10px 0; }
        .action-banner-text { font-size: 15px; font-weight: bold; color: #fbbf24; }
        
        .log-list { background: #0f172a; border-radius: 6px; padding: 8px; height: 90px; overflow-y: auto; font-family: monospace; font-size: 11px; color: #94a3b8; }
        .log-entry { margin-bottom: 3px; border-bottom: 1px solid #1e293b; padding-bottom: 2px; }
        
        .guide { width: 100%; max-width: 955px; background: #1e293b; padding: 12px; border-radius: 8px; margin-top: 15px; font-size: 13px; color: #94a3b8; text-align: center; border: 1px solid #334155; }
        .badge { display: inline-block; background: #334155; color: #f8fafc; padding: 4px 8px; border-radius: 4px; margin: 2px; font-weight: 500; font-size: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Hand Gesture Controller</h1>
        <p style="color:#94a3b8; font-size:13px;">Real-Time Robust Landmark Detection & Action Engine</p>
    </div>

    <div class="main-layout">
        <!-- Live Video -->
        <div class="camera-card">
            <div class="hud">
                <div>Gesture: <strong id="hud-gesture">No Hand</strong></div>
                <div>Action: <span id="hud-action">Ready</span></div>
                <div id="hud-fps" style="color:#94a3b8; font-family:monospace;">0 FPS</div>
            </div>
            <video id="webcam" playsinline></video>
            <canvas id="output_canvas" width="520" height="390"></canvas>
        </div>

        <!-- Working Media Player -->
        <div class="player-card">
            <div class="track-info">
                <div class="track-title" id="track-name">🎵 Track 1: Lo-Fi Beats</div>
                <div class="track-status" id="play-status">⏸️ Paused (Show Open Palm to Play)</div>
            </div>

            <div class="vol-container">
                <div class="vol-label">
                    <span>🔊 System Volume</span>
                    <span id="vol-text">70%</span>
                </div>
                <div class="vol-bar">
                    <div class="vol-fill" id="vol-bar-fill" style="width: 70%;"></div>
                </div>
            </div>

            <div class="action-banner">
                <div style="font-size: 11px; color:#94a3b8; text-transform:uppercase;">Last Executed Action</div>
                <div class="action-banner-text" id="action-banner-text">Waiting for gesture...</div>
            </div>

            <div>
                <div style="font-size: 12px; color: #94a3b8; margin-bottom: 4px;">Action Event History:</div>
                <div class="log-list" id="action-log">
                    <div class="log-entry">[Ready] Gesture Controller Initialized</div>
                </div>
            </div>
        </div>
    </div>

    <div class="guide">
        <strong>Gesture Action Guide:</strong>
        <span class="badge">👍 Thumbs Up = Volume +10%</span>
        <span class="badge">👎 Thumbs Down = Volume -10%</span>
        <span class="badge">✋ Open Palm = Play / Pause</span>
        <span class="badge">✌️ Two Fingers = Next Track</span>
        <span class="badge">✊ Fist = Stop / Mute</span>
    </div>

    <script>
        const videoElement = document.getElementById('webcam');
        const canvasElement = document.getElementById('output_canvas');
        const canvasCtx = canvasElement.getContext('2d', { alpha: false, desynchronized: true });
        
        const hudGesture = document.getElementById('hud-gesture');
        const hudAction = document.getElementById('hud-action');
        const hudFps = document.getElementById('hud-fps');
        const volText = document.getElementById('vol-text');
        const volFill = document.getElementById('vol-bar-fill');
        const trackName = document.getElementById('track-name');
        const playStatus = document.getElementById('play-status');
        const actionBanner = document.getElementById('action-banner-text');
        const actionLog = document.getElementById('action-log');

        let volume = 70;
        let isPlaying = false;
        let trackIndex = 1;
        const tracks = ["🎵 Track 1: Lo-Fi Study Beats", "🎵 Track 2: Chill Synthwave", "🎵 Track 3: Ambient Piano"];

        let lastActionTime = 0;
        const COOLDOWN_MS = 1200; // 1.2 second debounce

        // Web Audio Synthesizer for Real Audible Feedback
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        let bgOscillator = null;

        function playTone(freq, type = 'sine', duration = 0.15) {
            try {
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = type;
                osc.frequency.value = freq;
                gain.gain.setValueAtTime(volume / 200, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + duration);
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + duration);
            } catch (e) {}
        }

        function togglePlayPause() {
            isPlaying = !isPlaying;
            if (isPlaying) {
                playStatus.innerText = "▶️ Playing";
                playStatus.style.color = "#4ade80";
                playTone(440, 'triangle', 0.3);
            } else {
                playStatus.innerText = "⏸️ Paused";
                playStatus.style.color = "#94a3b8";
                playTone(220, 'triangle', 0.2);
            }
        }

        function changeVolume(delta) {
            volume = Math.min(100, Math.max(0, volume + delta));
            volText.innerText = volume + "%";
            volFill.style.width = volume + "%";
            playTone(300 + (volume * 4), 'sine', 0.1);
        }

        function nextTrack() {
            trackIndex = (trackIndex % tracks.length) + 1;
            trackName.innerText = tracks[trackIndex - 1];
            playTone(600, 'sine', 0.2);
        }

        function stopMute() {
            isPlaying = false;
            playStatus.innerText = "⏹️ Stopped";
            playStatus.style.color = "#ef4444";
            playTone(180, 'sawtooth', 0.25);
        }

        function logAction(name, action) {
            actionBanner.innerText = `${name} ➔ ${action}`;
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            const time = new Date().toLocaleTimeString();
            entry.innerText = `[${time}] ${name}: ${action}`;
            actionLog.prepend(entry);
        }

        function executeAction(gestureName) {
            const now = Date.now();
            if (now - lastActionTime < COOLDOWN_MS) return;

            if (gestureName === "Thumbs Up") {
                changeVolume(+10);
                logAction("👍 Thumbs Up", "Volume Up (+10%)");
                lastActionTime = now;
            } else if (gestureName === "Thumbs Down") {
                changeVolume(-10);
                logAction("👎 Thumbs Down", "Volume Down (-10%)");
                lastActionTime = now;
            } else if (gestureName === "Open Palm") {
                togglePlayPause();
                logAction("✋ Open Palm", isPlaying ? "Play Media" : "Pause Media");
                lastActionTime = now;
            } else if (gestureName === "Two Fingers") {
                nextTrack();
                logAction("✌️ Two Fingers", "Next Track");
                lastActionTime = now;
            } else if (gestureName === "Fist") {
                stopMute();
                logAction("✊ Fist", "Stop / Mute");
                lastActionTime = now;
            }
        }

        // EUCLIDEAN DISTANCE RECOGNITION (Angle & Rotation Invariant)
        function dist(p1, p2) {
            return Math.hypot(p1.x - p2.x, p1.y - p2.y);
        }

        function analyzeGesture(lm) {
            const wrist = lm[0];
            
            // 4 main fingers: Extended if tip distance to wrist > PIP joint distance to wrist
            const indexUp = dist(lm[8], wrist) > dist(lm[6], wrist) * 1.25;
            const middleUp = dist(lm[12], wrist) > dist(lm[10], wrist) * 1.25;
            const ringUp = dist(lm[16], wrist) > dist(lm[14], wrist) * 1.25;
            const pinkyUp = dist(lm[20], wrist) > dist(lm[18], wrist) * 1.25;

            // Thumb Extended (distance to index knuckle)
            const thumbExtended = dist(lm[4], lm[9]) > dist(lm[2], lm[9]) * 1.2;

            // All fingers curled (Fist, Thumbs Up, Thumbs Down)
            const fingersCurled = !indexUp && !middleUp && !ringUp && !pinkyUp;

            // 1. OPEN PALM: All 5 fingers extended
            if (indexUp && middleUp && ringUp && pinkyUp && thumbExtended) {
                return { name: "Open Palm", action: "Play / Pause" };
            }

            // 2. TWO FINGERS (Victory / Peace): Index & Middle extended, Ring & Pinky curled
            if (indexUp && middleUp && !ringUp && !pinkyUp) {
                return { name: "Two Fingers", action: "Next Track" };
            }

            // 3. THUMBS UP: Fingers curled, thumb pointing UPWARDS relative to knuckle
            if (fingersCurled && thumbExtended && lm[4].y < lm[2].y - 0.04) {
                return { name: "Thumbs Up", action: "Volume Up (+10%)" };
            }

            // 4. THUMBS DOWN: Fingers curled, thumb pointing DOWNWARDS relative to knuckle
            if (fingersCurled && thumbExtended && lm[4].y > lm[2].y + 0.04) {
                return { name: "Thumbs Down", action: "Volume Down (-10%)" };
            }

            // 5. FIST: All fingers curled, thumb tucked in
            if (fingersCurled && !thumbExtended) {
                return { name: "Fist", action: "Stop / Mute" };
            }

            return { name: "Unknown", action: "Hold steady" };
        }

        // Fast Skeleton Draw
        const CONNECTIONS = [
            [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],
            [5,9],[9,10],[10,11],[11,12],[9,13],[13,14],[14,15],[15,16],
            [13,17],[17,18],[18,19],[19,20],[0,17]
        ];

        function drawSkeleton(ctx, lm, w, h) {
            ctx.strokeStyle = "#22c55e";
            ctx.lineWidth = 3;
            ctx.beginPath();
            for (let i = 0; i < CONNECTIONS.length; i++) {
                const [a, b] = CONNECTIONS[i];
                ctx.moveTo(lm[a].x * w, lm[a].y * h);
                ctx.lineTo(lm[b].x * w, lm[b].y * h);
            }
            ctx.stroke();

            ctx.fillStyle = "#ef4444";
            for (let i = 0; i < lm.length; i++) {
                ctx.beginPath();
                ctx.arc(lm[i].x * w, lm[i].y * h, 4, 0, 2 * Math.PI);
                ctx.fill();
            }
        }

        let fpsCount = 0;
        let lastFpsTime = performance.now();
        let isProcessing = false;

        function onResults(results) {
            fpsCount++;
            const now = performance.now();
            if (now - lastFpsTime >= 1000) {
                hudFps.innerText = fpsCount + " FPS";
                fpsCount = 0;
                lastFpsTime = now;
            }

            canvasCtx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

            if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
                const landmarks = results.multiHandLandmarks[0];
                drawSkeleton(canvasCtx, landmarks, canvasElement.width, canvasElement.height);

                const res = analyzeGesture(landmarks);
                hudGesture.innerText = res.name;
                hudAction.innerText = res.action;

                if (res.name !== "Unknown") {
                    executeAction(res.name);
                }
            } else {
                hudGesture.innerText = "No Hand";
                hudAction.innerText = "Show Hand";
            }
            isProcessing = false;
        }

        const hands = new Hands({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
        });

        hands.setOptions({
            maxNumHands: 1,
            modelComplexity: 0,
            minDetectionConfidence: 0.65,
            minTrackingConfidence: 0.55
        });

        hands.onResults(onResults);

        const camera = new Camera(videoElement, {
            onFrame: async () => {
                if (!isProcessing) {
                    isProcessing = true;
                    await hands.send({ image: videoElement });
                }
            },
            width: 480,
            height: 360
        });

        camera.start();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    print("\n* AI Controller Live & Active on port 5000...")
    app.run(host='0.0.0.0', port=5000)
EOF
