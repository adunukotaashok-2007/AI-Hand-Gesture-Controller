"""
Hand Detector Module
====================
Uses MediaPipe to detect hands and extract 21 landmark points.

Why this is a separate class:
- Isolates the ML/AI detection logic
- If we want to switch from MediaPipe to another library, only this
  class changes
- Other classes don't need to know HOW detection works, just the results
- Demonstrates: Abstraction, Encapsulation

MediaPipe Hand Landmarks:
- Detects 21 points on each hand
- Each point has (x, y, z) coordinates
- Points are numbered 0-20:
    0  = Wrist
    4  = Thumb tip
    8  = Index finger tip
    12 = Middle finger tip
    16 = Ring finger tip
    20 = Pinky tip
"""

import cv2
import mediapipe as mp


class HandDetector:
    """
    Detects hands in an image and returns landmark positions.

    Uses Google's MediaPipe library which provides pre-trained
    hand detection models.

    Attributes:
        max_hands (int): Maximum number of hands to detect
        detection_confidence (float): Minimum confidence for detection
        tracking_confidence (float): Minimum confidence for tracking
        mp_hands: MediaPipe hands solution
        hands: MediaPipe hands detector object
        mp_draw: MediaPipe drawing utilities
    """

    # Class constants for landmark indices
    # These never change, so they're class-level constants
    WRIST = 0
    THUMB_TIP = 4
    THUMB_IP = 3
    THUMB_MCP = 2
    INDEX_TIP = 8
    INDEX_PIP = 6
    MIDDLE_TIP = 12
    MIDDLE_PIP = 10
    RING_TIP = 16
    RING_PIP = 14
    PINKY_TIP = 20
    PINKY_PIP = 18

    def __init__(self, max_hands=1, detection_confidence=0.7,
                 tracking_confidence=0.6):
        """
        Initialize the hand detector with MediaPipe.

        Args:
            max_hands (int): How many hands to detect (1 is enough for us)
            detection_confidence (float): How sure MediaPipe must be to
                                          detect a hand (0.0 to 1.0)
            tracking_confidence (float): How sure MediaPipe must be to
                                         keep tracking (0.0 to 1.0)

        Higher confidence = fewer false detections but might miss real hands
        Lower confidence = detects more but might have false positives

        0.7 is a good balance for college demo.
        """
        self.max_hands = max_hands
        self.detection_confidence = detection_confidence
        self.tracking_confidence = tracking_confidence

        # Initialize MediaPipe components
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,       # False = video mode (faster)
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_confidence,
            min_tracking_confidence=self.tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles

        print(f"[HandDetector] Initialized (max_hands={max_hands}, "
              f"detection_conf={detection_confidence})")

    def find_hands(self, frame, draw=True):
        """
        Detect hands in the given frame.

        Args:
            frame: BGR image from OpenCV (numpy array)
            draw: Whether to draw landmarks on the frame

        Returns:
            tuple: (frame_with_drawings, results)
                - frame: Original frame with hand landmarks drawn
                - results: MediaPipe detection results

        How it works:
        1. Convert BGR (OpenCV format) to RGB (MediaPipe format)
        2. Run MediaPipe hand detection
        3. If hands found and draw=True, draw the landmarks
        4. Return the modified frame and raw results
        """
        # MediaPipe needs RGB, but OpenCV gives BGR
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Run detection
        results = self.hands.process(rgb_frame)

        # Draw landmarks if hands were found
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the 21 points and connections between them
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw_styles.get_default_hand_landmarks_style(),
                    self.mp_draw_styles.get_default_hand_connections_style()
                )

        return frame, results

    def get_landmark_positions(self, frame, results, hand_index=0):
        """
        Extract (x, y) pixel positions for all 21 landmarks.

        Args:
            frame: The image frame (needed for pixel conversion)
            results: MediaPipe detection results
            hand_index: Which hand to get (0 = first detected hand)

        Returns:
            list: List of 21 (id, x, y) tuples, or empty list if no hand

        Why convert coordinates?
        - MediaPipe gives normalized coordinates (0.0 to 1.0)
        - We need pixel coordinates for display and calculation
        - Multiply by frame width/height to convert
        """
        landmark_list = []

        if results.multi_hand_landmarks:
            if hand_index < len(results.multi_hand_landmarks):
                hand = results.multi_hand_landmarks[hand_index]
                height, width, _ = frame.shape

                for landmark_id, landmark in enumerate(hand.landmark):
                    # Convert normalized (0-1) to pixel coordinates
                    pixel_x = int(landmark.x * width)
                    pixel_y = int(landmark.y * height)
                    landmark_list.append((landmark_id, pixel_x, pixel_y))

        return landmark_list

    def get_finger_states(self, landmark_list):
        """
        Determine which fingers are up (extended) or down (folded).

        Args:
            landmark_list: List of (id, x, y) for all 21 landmarks

        Returns:
            list: [thumb, index, middle, ring, pinky]
                  1 = finger is UP, 0 = finger is DOWN

        How finger detection works:
        - For fingers (index to pinky):
          Compare TIP position with PIP (second joint) position
          If TIP is ABOVE PIP (lower y value) → finger is UP
          If TIP is BELOW PIP (higher y value) → finger is DOWN

        - For thumb (special case):
          Compare TIP x-position with IP joint x-position
          Because thumb moves sideways, not up/down

        This is the KEY LOGIC for gesture recognition!
        """
        if len(landmark_list) < 21:
            return []

        finger_states = []

        # --- Thumb ---
        # Thumb is special: it moves left/right, not up/down
        # For right hand: thumb tip LEFT of thumb IP = thumb is up
        # We check x-coordinate difference
        thumb_tip_x = landmark_list[self.THUMB_TIP][1]
        thumb_ip_x = landmark_list[self.THUMB_IP][1]
        thumb_mcp_x = landmark_list[self.THUMB_MCP][1]

        # Use the direction from MCP to IP to determine hand orientation
        if thumb_mcp_x < thumb_ip_x:
            # Right hand (or left hand palm facing camera)
            finger_states.append(1 if thumb_tip_x > thumb_ip_x else 0)
        else:
            # Left hand (or right hand palm facing camera)
            finger_states.append(1 if thumb_tip_x < thumb_ip_x else 0)

        # --- Index Finger ---
        # Tip (landmark 8) above PIP joint (landmark 6) means finger is up
        finger_states.append(
            1 if landmark_list[self.INDEX_TIP][2] <
                 landmark_list[self.INDEX_PIP][2] else 0
        )

        # --- Middle Finger ---
        finger_states.append(
            1 if landmark_list[self.MIDDLE_TIP][2] <
                 landmark_list[self.MIDDLE_PIP][2] else 0
        )

        # --- Ring Finger ---
        finger_states.append(
            1 if landmark_list[self.RING_TIP][2] <
                 landmark_list[self.RING_PIP][2] else 0
        )

        # --- Pinky Finger ---
        finger_states.append(
            1 if landmark_list[self.PINKY_TIP][2] <
                 landmark_list[self.PINKY_PIP][2] else 0
        )

        return finger_states

    def release(self):
        """Release MediaPipe resources."""
        self.hands.close()
        print("[HandDetector] Released successfully")
