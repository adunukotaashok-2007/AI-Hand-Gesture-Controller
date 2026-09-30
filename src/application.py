"""
Application Module
==================
Main orchestrator that ties all classes together.

Why this is a separate class:
- Central control point for the entire application
- Manages the main loop (read frame → detect → recognize → act)
- Handles UI display (drawing text on screen)
- Clean startup and shutdown procedures
- Demonstrates: Composition (has-a relationships), Facade pattern

This class uses COMPOSITION:
- Application HAS-A Camera
- Application HAS-A HandDetector
- Application HAS-A GestureRecognizer
- Application HAS-A ActionController
- Application HAS-A GestureLogger
"""

import cv2
import time
from src.camera import Camera
from src.hand_detector import HandDetector
from src.gesture_recognizer import GestureRecognizer
from src.action_controller import ActionController
from src.gesture_logger import GestureLogger


class Application:
    """
    Main application class that runs the hand gesture controller.

    This class:
    1. Creates all necessary objects (Camera, Detector, etc.)
    2. Runs the main processing loop
    3. Displays results on screen
    4. Handles cleanup on exit

    Attributes:
        camera: Camera object for webcam
        detector: HandDetector for finding hands
        recognizer: GestureRecognizer for identifying gestures
        controller: ActionController for executing actions
        logger: GestureLogger for database logging
        window_name: Name of the OpenCV display window
        fps_time: For calculating frames per second
    """

    def __init__(self):
        """
        Initialize all components of the application.

        Order matters:
        1. Camera first (we need frames for everything else)
        2. HandDetector (processes frames)
        3. GestureRecognizer (interprets detection results)
        4. ActionController (executes actions)
        5. GestureLogger (logs results)
        """
        print("\n--- Initializing Components ---")

        try:
            self.camera = Camera(camera_index=0, width=640, height=480)
        except RuntimeError as e:
            print(f"\n{e}")
            print("\nCannot start without a camera. Exiting.")
            raise SystemExit(1)

        self.detector = HandDetector(
            max_hands=1,
            detection_confidence=0.7,
            tracking_confidence=0.6
        )
        self.recognizer = GestureRecognizer()
        self.controller = ActionController(cooldown_time=1.5)
        self.logger = GestureLogger()

        self.window_name = "AI Hand Gesture Controller"
        self.fps_time = time.time()
        self.current_gesture = "None"
        self.current_action = "Waiting..."
        self.action_executed = False

        print("\n--- All Components Ready ---\n")
        self._print_gesture_guide()

    def _print_gesture_guide(self):
        """Print a guide of all supported gestures to the console."""
        print("Supported Gestures:")
        print("-" * 45)
        print(f"  {'Gesture':<15} {'Action':<20} {'Fingers'}")
        print("-" * 45)
        gestures = self.recognizer.get_all_gestures()
        for g in gestures:
            note = g.get('note', '')
            fingers = str(g['finger_states'])
            print(f"  {g['name']:<15} {g['action']:<20} {fingers} {note}")
        print("-" * 45)
        print()

    def run(self):
        """
        Main application loop.

        This is the HEART of the application. It runs continuously until
        the user presses 'q'.

        Loop steps:
        1. Read a frame from the camera
        2. Detect hands in the frame
        3. Get landmark positions
        4. Determine finger states
        5. Recognize the gesture
        6. Execute the corresponding action
        7. Log the gesture
        8. Display everything on screen
        9. Check for quit key
        """
        print("Application running. Press 'q' to quit.\n")

        try:
            while True:
                # Step 1: Read frame
                success, frame = self.camera.read_frame()
                if not success:
                    print("[App] Failed to read frame. Retrying...")
                    continue

                # Step 2: Detect hands and draw landmarks
                frame, results = self.detector.find_hands(frame, draw=True)

                # Step 3: Get landmark positions
                landmark_list = self.detector.get_landmark_positions(
                    frame, results
                )

                # Steps 4-7: Process if hand is detected
                if landmark_list:
                    # Step 4: Get finger states
                    finger_states = self.detector.get_finger_states(
                        landmark_list
                    )

                    if finger_states:
                        # Step 5: Recognize gesture
                        gesture = self.recognizer.recognize(
                            finger_states, landmark_list
                        )
                        self.current_gesture = gesture.name
                        self.current_action = gesture.action

                        # Step 6: Execute action (with cooldown check)
                        if gesture.name != "Unknown":
                            self.action_executed = self.controller.execute(
                                gesture
                            )

                            # Step 7: Log to database (only when executed)
                            if self.action_executed:
                                self.logger.log_gesture(gesture)
                else:
                    self.current_gesture = "No Hand Detected"
                    self.current_action = "Show your hand"
                    self.action_executed = False

                # Step 8: Draw UI elements on frame
                frame = self._draw_ui(frame)

                # Display the frame
                cv2.imshow(self.window_name, frame)

                # Step 9: Check for quit key (wait 1ms for key press)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\n[App] Quit key pressed. Shutting down...")
                    break

        except KeyboardInterrupt:
            print("\n[App] Keyboard interrupt. Shutting down...")
        finally:
            self._cleanup()

    def _draw_ui(self, frame):
        """
        Draw information overlay on the video frame.

        Displays:
        - Current gesture name
        - Current action
        - FPS counter
        - Cooldown indicator
        - Gesture guide

        Args:
            frame: The video frame to draw on

        Returns:
            frame: Frame with UI elements drawn
        """
        height, width, _ = frame.shape

        # --- Background panel for text (semi-transparent effect) ---
        # Draw a dark rectangle at the top for better text visibility
        cv2.rectangle(frame, (0, 0), (width, 120), (40, 40, 40), -1)

        # --- Gesture Name ---
        color = (0, 255, 0) if self.current_gesture != "Unknown" and \
                               self.current_gesture != "No Hand Detected" \
                else (0, 0, 255)
        cv2.putText(
            frame,
            f"Gesture: {self.current_gesture}",
            (10, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            color,
            2
        )

        # --- Action ---
        action_color = (0, 255, 255) if self.action_executed \
            else (200, 200, 200)
        action_text = f"Action: {self.current_action}"
        if self.action_executed:
            action_text += " [EXECUTED]"
        cv2.putText(
            frame,
            action_text,
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            action_color,
            2
        )

        # --- FPS ---
        current_time = time.time()
        fps = 1.0 / (current_time - self.fps_time) if \
            (current_time - self.fps_time) > 0 else 0
        self.fps_time = current_time
        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (width - 120, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )

        # --- Cooldown indicator ---
        if self.current_gesture not in ["Unknown", "No Hand Detected", "None"]:
            remaining = self.controller.get_cooldown_remaining(
                self.current_gesture
            )
            if remaining > 0:
                cv2.putText(
                    frame,
                    f"Cooldown: {remaining}s",
                    (width - 200, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 165, 255),
                    2
                )

        # --- Gesture Guide at bottom ---
        guide_y = height - 100
        cv2.rectangle(frame, (0, guide_y - 10), (width, height),
                       (40, 40, 40), -1)
        guides = [
            "Thumbs Up: Vol+",
            "Thumbs Down: Vol-",
            "Open Palm: Play/Pause",
            "Two Fingers: Next",
            "Fist: Prev/Stop"
        ]
        cv2.putText(frame, "Gesture Guide:", (10, guide_y + 15),
                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        for i, guide in enumerate(guides):
            x_pos = 10 + (i % 3) * 210
            y_pos = guide_y + 40 + (i // 3) * 25
            cv2.putText(frame, guide, (x_pos, y_pos),
                         cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180, 180, 180), 1)

        # --- Instructions ---
        cv2.putText(
            frame,
            "Press 'Q' to quit",
            (10, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (150, 150, 150),
            1
        )

        return frame

    def _cleanup(self):
        """
        Clean up all resources when application exits.

        Why cleanup is important:
        - Release webcam so other apps can use it
        - Close database connection properly
        - Close OpenCV windows
        - Release MediaPipe resources
        - Prevent resource leaks
        """
        print("\n--- Cleaning Up ---")

        # Print gesture statistics before closing
        stats = self.logger.get_gesture_statistics()
        total = self.logger.get_gesture_count()
        if stats:
            print(f"\nSession Statistics (Total: {total} gestures):")
            for name, count in stats:
                print(f"  {name}: {count} times")

        self.camera.release()
        self.detector.release()
        self.logger.close()
        cv2.destroyAllWindows()

        print("\n--- Application Closed ---")
