"""
Camera Module
=============
Handles all webcam-related operations.

Why this is a separate class:
- Isolates hardware interaction (webcam) from application logic
- If we want to switch to a different camera or video file, we only
  change this class
- Error handling for camera issues is in one place
- Demonstrates OOP concepts: Encapsulation, Abstraction
"""

import cv2


class Camera:
    """
    Manages webcam capture operations.

    This class wraps OpenCV's VideoCapture to provide a clean interface
    for reading frames from the webcam.

    Attributes:
        camera_index (int): Which camera to use (0 = default webcam)
        width (int): Frame width in pixels
        height (int): Frame height in pixels
        cap (cv2.VideoCapture): OpenCV capture object
    """

    def __init__(self, camera_index=0, width=640, height=480):
        """
        Initialize the camera.

        Args:
            camera_index (int): Camera device index (0 for default webcam)
            width (int): Desired frame width
            height (int): Desired frame height

        What happens here:
        1. Store the camera settings
        2. Open the webcam connection
        3. Set the resolution
        4. Check if camera opened successfully
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.cap = None

        # Open the camera
        self._initialize_camera()

    def _initialize_camera(self):
        """
        Private method to set up the camera.

        Why private (underscore prefix)?
        - This is an internal detail that other classes don't need to call
        - Only Camera class itself uses this method
        - Demonstrates encapsulation

        Error Handling:
        - If camera doesn't open, raise a clear error message
        - This prevents confusing errors later in the program
        """
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"ERROR: Cannot open camera (index={self.camera_index}). "
                f"Please check:\n"
                f"  1. Is your webcam connected?\n"
                f"  2. Is another application using the camera?\n"
                f"  3. Try a different camera_index (0, 1, 2...)"
            )

        # Set resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        print(f"[Camera] Opened successfully (index={self.camera_index}, "
              f"{self.width}x{self.height})")

    def read_frame(self):
        """
        Read one frame from the webcam.

        Returns:
            tuple: (success: bool, frame: numpy array)
                - success: True if frame was captured
                - frame: The image as a numpy array (or None if failed)

        Why return a tuple?
        - Caller can check if reading was successful
        - Prevents crashes from using a None frame
        """
        if self.cap is None or not self.cap.isOpened():
            return False, None

        success, frame = self.cap.read()

        if not success:
            print("[Camera] WARNING: Failed to read frame")
            return False, None

        # Flip horizontally for mirror effect (more natural for user)
        frame = cv2.flip(frame, 1)

        return True, frame

    def is_opened(self):
        """Check if camera is still open and working."""
        return self.cap is not None and self.cap.isOpened()

    def release(self):
        """
        Release the camera resource.

        Why this is important:
        - Frees the webcam so other applications can use it
        - Prevents resource leaks
        - Should always be called when done
        """
        if self.cap is not None:
            self.cap.release()
            print("[Camera] Released successfully")

    def __del__(self):
        """
        Destructor - automatically releases camera when object is deleted.

        Why use a destructor?
        - Safety net in case release() isn't called manually
        - Prevents webcam from staying locked
        """
        self.release()
