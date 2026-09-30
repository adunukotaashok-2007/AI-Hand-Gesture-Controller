"""
Gesture Recognizer Module
=========================
Analyzes finger states to identify which gesture is being performed.

Why this is a separate class:
- Separates the DETECTION of hands (HandDetector) from the
  INTERPRETATION of gestures (GestureRecognizer)
- Easy to add new gestures without changing detection code
- Single Responsibility Principle: this class ONLY recognizes patterns
- Demonstrates: Abstraction, Single Responsibility

Gesture Definitions (finger states: [thumb, index, middle, ring, pinky]):
- Thumbs Up:    [1, 0, 0, 0, 0] - Only thumb up
- Thumbs Down:  [0, 0, 0, 0, 0] with thumb pointing down (special check)
- Open Palm:    [1, 1, 1, 1, 1] - All fingers up
- Two Fingers:  [0, 1, 1, 0, 0] - Index and middle up (peace/victory)
- Fist:         [0, 0, 0, 0, 0] - All fingers down
"""

from src.gesture import Gesture


class GestureRecognizer:
    """
    Recognizes hand gestures from finger state patterns.

    This class contains the logic to map finger positions to
    meaningful gesture names.

    Attributes:
        gesture_map (dict): Maps finger patterns to gesture info
    """

    # Gesture name constants - prevents typos
    THUMBS_UP = "Thumbs Up"
    THUMBS_DOWN = "Thumbs Down"
    OPEN_PALM = "Open Palm"
    TWO_FINGERS = "Two Fingers"
    FIST = "Fist"
    UNKNOWN = "Unknown"

    def __init__(self):
        """
        Initialize the gesture recognizer.

        The gesture_map dictionary defines:
        - Key: tuple of finger states (thumb, index, middle, ring, pinky)
        - Value: dict with gesture name and corresponding action

        Why use a dictionary?
        - O(1) lookup time (very fast)
        - Easy to add/remove gestures
        - Clean and readable
        """
        self.gesture_map = {
            # (thumb, index, middle, ring, pinky): {name, action}
            (1, 0, 0, 0, 0): {
                "name": self.THUMBS_UP,
                "action": "Volume Up"
            },
            (1, 1, 1, 1, 1): {
                "name": self.OPEN_PALM,
                "action": "Play/Pause"
            },
            (0, 1, 1, 0, 0): {
                "name": self.TWO_FINGERS,
                "action": "Next"
            },
            (0, 0, 0, 0, 0): {
                "name": self.FIST,
                "action": "Stop/Previous"
            },
        }

        print(f"[GestureRecognizer] Initialized with "
              f"{len(self.gesture_map) + 1} gestures")

    def recognize(self, finger_states, landmark_list=None):
        """
        Identify the gesture from finger states.

        Args:
            finger_states (list): [thumb, index, middle, ring, pinky]
                                  where 1=up, 0=down
            landmark_list (list): Full landmark positions (needed for
                                  thumbs down detection)

        Returns:
            Gesture: A Gesture object with name and action

        How recognition works:
        1. Convert finger_states list to tuple (for dictionary lookup)
        2. Check special cases first (Thumbs Down)
        3. Look up the pattern in gesture_map
        4. Return matching Gesture or "Unknown"
        """
        if not finger_states or len(finger_states) != 5:
            return Gesture(name=self.UNKNOWN, action="None",
                           finger_states=finger_states)

        # Convert to tuple for dictionary lookup
        state_tuple = tuple(finger_states)

        # --- Special Case: Thumbs Down ---
        # Thumbs down has same finger states as Fist [0,0,0,0,0]
        # BUT the thumb tip is BELOW the thumb MCP joint
        # We need landmark positions to distinguish them
        if state_tuple == (0, 0, 0, 0, 0) and landmark_list:
            if self._is_thumbs_down(landmark_list):
                return Gesture(
                    name=self.THUMBS_DOWN,
                    action="Volume Down",
                    finger_states=finger_states
                )

        # --- Normal Lookup ---
        if state_tuple in self.gesture_map:
            gesture_info = self.gesture_map[state_tuple]
            return Gesture(
                name=gesture_info["name"],
                action=gesture_info["action"],
                finger_states=finger_states
            )

        # --- Unknown Gesture ---
        return Gesture(name=self.UNKNOWN, action="None",
                       finger_states=finger_states)

    def _is_thumbs_down(self, landmark_list):
        """
        Check if the hand is showing a "Thumbs Down" gesture.

        Logic:
        - In thumbs down, the thumb tip (landmark 4) is BELOW
          the thumb MCP joint (landmark 2) in y-coordinate
        - Also, the thumb should be somewhat extended
          (tip far from wrist)

        Args:
            landmark_list: List of (id, x, y) for all landmarks

        Returns:
            bool: True if thumbs down is detected

        Note: In screen coordinates, DOWN means LARGER y value
        """
        if len(landmark_list) < 21:
            return False

        thumb_tip_y = landmark_list[4][2]    # Thumb tip y
        thumb_mcp_y = landmark_list[2][2]    # Thumb MCP y
        wrist_y = landmark_list[0][2]        # Wrist y
        index_mcp_y = landmark_list[5][2]    # Index finger MCP y

        # Thumb tip should be below the MCP joint (larger y)
        thumb_pointing_down = thumb_tip_y > thumb_mcp_y

        # Thumb should be somewhat extended (not just a fist)
        thumb_extended = abs(thumb_tip_y - thumb_mcp_y) > 20

        # All other fingers should be curled
        # (already checked as [0,0,0,0,0] before calling this)

        return thumb_pointing_down and thumb_extended

    def get_all_gestures(self):
        """
        Get a list of all supported gestures.

        Returns:
            list: List of dicts with gesture names and actions

        Useful for:
        - Displaying help information
        - Testing all gestures
        - Documentation
        """
        gestures = []
        for state, info in self.gesture_map.items():
            gestures.append({
                "finger_states": state,
                "name": info["name"],
                "action": info["action"]
            })
        # Add thumbs down (special case)
        gestures.append({
            "finger_states": (0, 0, 0, 0, 0),
            "name": self.THUMBS_DOWN,
            "action": "Volume Down",
            "note": "With thumb pointing downward"
        })
        return gestures
