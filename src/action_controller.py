"""
Action Controller Module
========================
Executes computer actions based on recognized gestures.

Why this is a separate class:
- Separates gesture recognition from action execution
- Cooldown/debounce logic is centralized here
- Easy to change what each gesture does without touching recognition
- Platform-specific code (Windows volume control) is isolated
- Demonstrates: Encapsulation, Single Responsibility

Cooldown/Debounce Explanation:
- Without cooldown: holding "Thumbs Up" for 1 second would trigger
  "Volume Up" ~30 times (once per frame at 30 FPS)!
- With cooldown: it triggers once, then waits 1.5 seconds before
  allowing the same action again
- This makes the system usable and predictable
"""

import time
import pyautogui

# Try to import pycaw for Windows volume control
# If not on Windows or pycaw not installed, fall back to pyautogui
try:
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
    print("[ActionController] pycaw not available, using keyboard shortcuts "
          "for volume control")


class ActionController:
    """
    Maps gestures to system actions and handles cooldown timing.

    Attributes:
        cooldown_time (float): Minimum seconds between repeated actions
        last_action_time (dict): Tracks when each action was last performed
        volume_interface: Windows audio interface (if available)
        action_map (dict): Maps gesture names to action methods
    """

    def __init__(self, cooldown_time=1.5):
        """
        Initialize the action controller.

        Args:
            cooldown_time (float): Seconds to wait before same gesture
                                   can trigger again (default: 1.5s)

        Why 1.5 seconds?
        - Fast enough to feel responsive
        - Slow enough to prevent accidental repeats
        - Good balance for a college demo
        """
        self.cooldown_time = cooldown_time
        self.last_action_time = {}  # {action_name: timestamp}
        self.last_gesture = ""

        # Initialize volume control (Windows-specific)
        self.volume_interface = None
        if PYCAW_AVAILABLE:
            self._init_volume_control()

        # Map gesture names to their action methods
        # Using a dictionary of methods (Strategy Pattern)
        self.action_map = {
            "Thumbs Up": self._volume_up,
            "Thumbs Down": self._volume_down,
            "Open Palm": self._play_pause,
            "Two Fingers": self._next_action,
            "Fist": self._stop_previous,
        }

        # Disable pyautogui's fail-safe (moving mouse to corner stops it)
        pyautogui.FAILSAFE = False

        print(f"[ActionController] Initialized (cooldown={cooldown_time}s)")

    def _init_volume_control(self):
        """
        Initialize Windows volume control using pycaw.

        Why pycaw instead of pyautogui for volume?
        - pycaw gives precise volume control (set exact percentage)
        - pyautogui can only simulate key presses (less precise)
        - pycaw doesn't show the volume overlay (cleaner for demo)
        """
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None
            )
            self.volume_interface = cast(interface,
                                         POINTER(IAudioEndpointVolume))
            print("[ActionController] Volume control initialized (pycaw)")
        except Exception as e:
            print(f"[ActionController] Volume control failed: {e}")
            self.volume_interface = None

    def execute(self, gesture):
        """
        Execute the action for a recognized gesture.

        Args:
            gesture (Gesture): The recognized gesture object

        Returns:
            bool: True if action was executed, False if on cooldown

        Flow:
        1. Check if gesture has a mapped action
        2. Check if cooldown period has passed
        3. If yes → execute the action and update timestamp
        4. If no → skip (return False)
        """
        if gesture.name == "Unknown" or gesture.name not in self.action_map:
            return False

        # Check cooldown
        if not self._is_cooldown_passed(gesture.name):
            return False

        # Execute the action
        action_method = self.action_map[gesture.name]
        action_method()

        # Update cooldown timestamp
        self.last_action_time[gesture.name] = time.time()
        self.last_gesture = gesture.name

        return True

    def _is_cooldown_passed(self, gesture_name):
        """
        Check if enough time has passed since the last action.

        Args:
            gesture_name (str): Name of the gesture to check

        Returns:
            bool: True if cooldown has passed (can execute)

        How it works:
        - Look up when this gesture was last triggered
        - If never triggered → return True (can execute)
        - If triggered recently → check if cooldown_time has passed
        """
        if gesture_name not in self.last_action_time:
            return True

        elapsed = time.time() - self.last_action_time[gesture_name]
        return elapsed >= self.cooldown_time

    def _volume_up(self):
        """
        Increase system volume.

        Two methods:
        1. pycaw (Windows): Direct volume control, increase by 10%
        2. pyautogui fallback: Simulate 'volume up' key press
        """
        print("[Action] 🔊 Volume Up")
        if self.volume_interface:
            try:
                current = self.volume_interface.GetMasterVolumeLevelScalar()
                new_volume = min(1.0, current + 0.1)  # +10%, max 100%
                self.volume_interface.SetMasterVolumeLevelScalar(
                    new_volume, None
                )
            except Exception:
                pyautogui.press('volumeup')
        else:
            pyautogui.press('volumeup')

    def _volume_down(self):
        """
        Decrease system volume.

        Similar to volume_up but decreases by 10%.
        """
        print("[Action] 🔉 Volume Down")
        if self.volume_interface:
            try:
                current = self.volume_interface.GetMasterVolumeLevelScalar()
                new_volume = max(0.0, current - 0.1)  # -10%, min 0%
                self.volume_interface.SetMasterVolumeLevelScalar(
                    new_volume, None
                )
            except Exception:
                pyautogui.press('volumedown')
        else:
            pyautogui.press('volumedown')

    def _play_pause(self):
        """
        Toggle Play/Pause for media.

        Uses the 'playpause' media key.
        Works with most media players (Spotify, YouTube, VLC, etc.)
        """
        print("[Action] ⏯️  Play/Pause")
        pyautogui.press('playpause')

    def _next_action(self):
        """
        Go to next track/slide.

        Uses 'nexttrack' media key for music.
        For presentations, you could change this to 'right' arrow.
        """
        print("[Action] ⏭️  Next Track/Slide")
        pyautogui.press('nexttrack')

    def _stop_previous(self):
        """
        Stop or go to previous track.

        Uses 'prevtrack' media key.
        """
        print("[Action] ⏮️  Previous/Stop")
        pyautogui.press('prevtrack')

    def get_cooldown_remaining(self, gesture_name):
        """
        Get remaining cooldown time for a gesture.

        Returns:
            float: Seconds remaining (0 if cooldown passed)
        """
        if gesture_name not in self.last_action_time:
            return 0.0
        elapsed = time.time() - self.last_action_time[gesture_name]
        remaining = max(0.0, self.cooldown_time - elapsed)
        return round(remaining, 1)
