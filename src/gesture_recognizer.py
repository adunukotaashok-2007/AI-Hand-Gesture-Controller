"""
Gesture Recognizer - Maps finger states to gesture names.
"""

from src.gesture import Gesture


class GestureRecognizer:
    THUMBS_UP = "Thumbs Up"
    THUMBS_DOWN = "Thumbs Down"
    OPEN_PALM = "Open Palm"
    TWO_FINGERS = "Two Fingers"
    FIST = "Fist"
    UNKNOWN = "Unknown"

    def __init__(self):
        self.gesture_map = {
            (1, 0, 0, 0, 0): {"name": self.THUMBS_UP, "action": "Volume Up"},
            (1, 1, 1, 1, 1): {"name": self.OPEN_PALM, "action": "Play/Pause"},
            (0, 1, 1, 0, 0): {"name": self.TWO_FINGERS, "action": "Next"},
            (0, 0, 0, 0, 0): {"name": self.FIST, "action": "Stop/Previous"},
        }
        print(f"[GestureRecognizer] Initialized ({len(self.gesture_map)+1} gestures)")

    def recognize(self, finger_states, landmark_list=None):
        if not finger_states or len(finger_states) != 5:
            return Gesture(name=self.UNKNOWN, action="None",
                           finger_states=finger_states)

        state_tuple = tuple(finger_states)

        # Special case: Thumbs Down vs Fist
        if state_tuple == (0, 0, 0, 0, 0) and landmark_list:
            if self._is_thumbs_down(landmark_list):
                return Gesture(name=self.THUMBS_DOWN, action="Volume Down",
                               finger_states=finger_states)

        if state_tuple in self.gesture_map:
            info = self.gesture_map[state_tuple]
            return Gesture(name=info["name"], action=info["action"],
                           finger_states=finger_states)

        return Gesture(name=self.UNKNOWN, action="None",
                       finger_states=finger_states)

    def _is_thumbs_down(self, landmark_list):
        if len(landmark_list) < 21:
            return False
        thumb_tip_y = landmark_list[4][2]
        thumb_mcp_y = landmark_list[2][2]
        return (thumb_tip_y > thumb_mcp_y) and \
               (abs(thumb_tip_y - thumb_mcp_y) > 20)

    def get_all_gestures(self):
        gestures = []
        for state, info in self.gesture_map.items():
            gestures.append({
                "finger_states": state,
                "name": info["name"],
                "action": info["action"]
            })
        gestures.append({
            "finger_states": (0, 0, 0, 0, 0),
            "name": self.THUMBS_DOWN,
            "action": "Volume Down",
            "note": "Thumb pointing down"
        })
        return gestures
