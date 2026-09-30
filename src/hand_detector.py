"""
Hand Detector Module - Uses MediaPipe to find 21 hand landmarks.
"""

import cv2
import mediapipe as mp


class HandDetector:
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
        self.max_hands = max_hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=self.max_hands,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_draw_styles = mp.solutions.drawing_styles
        print(f"[HandDetector] Initialized")

    def find_hands(self, frame, draw=True):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks and draw:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw_styles.get_default_hand_landmarks_style(),
                    self.mp_draw_styles.get_default_hand_connections_style()
                )
        return frame, results

    def get_landmark_positions(self, frame, results, hand_index=0):
        landmark_list = []
        if results.multi_hand_landmarks:
            if hand_index < len(results.multi_hand_landmarks):
                hand = results.multi_hand_landmarks[hand_index]
                h, w, _ = frame.shape
                for lm_id, lm in enumerate(hand.landmark):
                    px = int(lm.x * w)
                    py = int(lm.y * h)
                    landmark_list.append((lm_id, px, py))
        return landmark_list

    def get_finger_states(self, landmark_list):
        if len(landmark_list) < 21:
            return []
        states = []

        # Thumb (x-axis)
        thumb_tip_x = landmark_list[self.THUMB_TIP][1]
        thumb_ip_x = landmark_list[self.THUMB_IP][1]
        thumb_mcp_x = landmark_list[self.THUMB_MCP][1]
        if thumb_mcp_x < thumb_ip_x:
            states.append(1 if thumb_tip_x > thumb_ip_x else 0)
        else:
            states.append(1 if thumb_tip_x < thumb_ip_x else 0)

        # Index
        states.append(
            1 if landmark_list[self.INDEX_TIP][2] <
                 landmark_list[self.INDEX_PIP][2] else 0)
        # Middle
        states.append(
            1 if landmark_list[self.MIDDLE_TIP][2] <
                 landmark_list[self.MIDDLE_PIP][2] else 0)
        # Ring
        states.append(
            1 if landmark_list[self.RING_TIP][2] <
                 landmark_list[self.RING_PIP][2] else 0)
        # Pinky
        states.append(
            1 if landmark_list[self.PINKY_TIP][2] <
                 landmark_list[self.PINKY_PIP][2] else 0)

        return states

    def release(self):
        self.hands.close()
        print("[HandDetector] Released")
