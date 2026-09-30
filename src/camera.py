"""
Camera Module - Handles webcam capture using OpenCV.
"""

import cv2


class Camera:
    def __init__(self, camera_index=0, width=640, height=480):
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None
        self._initialize_camera()

    def _initialize_camera(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(
                f"Cannot open camera (index={self.camera_index}). "
                f"Check: 1) Webcam connected? 2) Close Zoom/Teams. "
                f"3) Try camera_index=1"
            )
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        print(f"[Camera] Opened ({self.width}x{self.height})")

    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return False, None
        success, frame = self.cap.read()
        if not success:
            return False, None
        frame = cv2.flip(frame, 1)
        return True, frame

    def is_opened(self):
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        if self.cap is not None:
            self.cap.release()
            print("[Camera] Released")

    def __del__(self):
        self.release()
