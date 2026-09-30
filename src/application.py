"""
Application - Main orchestrator that connects all modules.
"""

import cv2
import time
from src.camera import Camera
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.action_controller import ActionController
from src.gesture_logger import GestureLogger


class Application:
    def __init__(self):
        print("\n--- Initializing ---")
        try:
            self.camera = Camera(camera_index=0, width=640, height=480)
        except RuntimeError as e:
            print(f"\n{e}")
            raise SystemExit(1)

        self.detector = HandDetector()
        self.recognizer = GestureRecognizer()
        self.controller = ActionController(cooldown_time=1.5)
        self.logger = GestureLogger()

        self.window_name = "AI Hand Gesture Controller"
        self.fps_time = time.time()
        self.current_gesture = "None"
        self.current_action = "Waiting..."
        self.action_executed = False

        print("\n--- Ready! ---\n")
        self._print_guide()

    def _print_guide(self):
        print("Gestures:")
        print("  Thumbs Up    -> Volume Up")
        print("  Thumbs Down  -> Volume Down")
        print("  Open Palm    -> Play/Pause")
        print("  Two Fingers  -> Next")
        print("  Fist         -> Previous/Stop")
        print()

    def run(self):
        print("Running. Press 'q' to quit.\n")
        try:
            while True:
                success, frame = self.camera.read_frame()
                if not success:
                    continue

                frame, results = self.detector.find_hands(frame, draw=True)
                landmarks = self.detector.get_landmark_positions(
                    frame, results)

                if landmarks:
                    fingers = self.detector.get_finger_states(landmarks)
                    if fingers:
                        gesture = self.recognizer.recognize(
                            fingers, landmarks)
                        self.current_gesture = gesture.name
                        self.current_action = gesture.action

                        if gesture.name != "Unknown":
                            self.action_executed = \
                                self.controller.execute(gesture)
                            if self.action_executed:
                                self.logger.log_gesture(gesture)
                else:
                    self.current_gesture = "No Hand Detected"
                    self.current_action = "Show your hand"
                    self.action_executed = False

                frame = self._draw_ui(frame)
                cv2.imshow(self.window_name, frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\nQuitting...")
                    break

        except KeyboardInterrupt:
            print("\nInterrupted.")
        finally:
            self._cleanup()

    def _draw_ui(self, frame):
        h, w, _ = frame.shape

        # Top panel
        cv2.rectangle(frame, (0, 0), (w, 110), (40, 40, 40), -1)

        # Gesture name
        color = (0, 255, 0) if self.current_gesture not in \
                ["Unknown", "No Hand Detected", "None"] else (0, 0, 255)
        cv2.putText(frame, f"Gesture: {self.current_gesture}",
                     (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Action
        ac = (0, 255, 255) if self.action_executed else (200, 200, 200)
        txt = f"Action: {self.current_action}"
        if self.action_executed:
            txt += " [DONE]"
        cv2.putText(frame, txt, (10, 70),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, ac, 2)

        # FPS
        now = time.time()
        fps = 1.0 / (now - self.fps_time) if (now - self.fps_time) > 0 else 0
        self.fps_time = now
        cv2.putText(frame, f"FPS: {int(fps)}", (w - 120, 35),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Cooldown
        if self.current_gesture not in \
           ["Unknown", "No Hand Detected", "None"]:
            rem = self.controller.get_cooldown_remaining(
                self.current_gesture)
            if rem > 0:
                cv2.putText(frame, f"Cooldown: {rem}s", (w - 200, 70),
                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

        # Bottom guide
        gy = h - 60
        cv2.rectangle(frame, (0, gy - 5), (w, h), (40, 40, 40), -1)
        guides = ["ThumbsUp:Vol+", "ThumbsDown:Vol-",
                  "Palm:Play", "2Fingers:Next", "Fist:Prev"]
        for i, g in enumerate(guides):
            cv2.putText(frame, g, (10 + i * 125, gy + 25),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        cv2.putText(frame, "Press Q to quit", (10, 100),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)
        return frame

    def _cleanup(self):
        print("\n--- Cleanup ---")
        stats = self.logger.get_gesture_statistics()
        total = self.logger.get_gesture_count()
        if stats:
            print(f"Session Stats (Total: {total}):")
            for name, count in stats:
                print(f"  {name}: {count}x")
        self.camera.release()
        self.detector.release()
        self.logger.close()
        cv2.destroyAllWindows()
        print("--- Done ---")
