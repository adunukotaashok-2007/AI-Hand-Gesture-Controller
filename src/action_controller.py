"""
Action Controller - Executes computer actions with cooldown.
"""

import time
import platform
import pyautogui

PYCAW_AVAILABLE = False
if platform.system() == "Windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except ImportError:
        pass


class ActionController:
    def __init__(self, cooldown_time=1.5):
        self.cooldown_time = cooldown_time
        self.last_action_time = {}
        self.last_gesture = ""
        self.volume_interface = None

        if PYCAW_AVAILABLE:
            self._init_volume()

        self.action_map = {
            "Thumbs Up": self._volume_up,
            "Thumbs Down": self._volume_down,
            "Open Palm": self._play_pause,
            "Two Fingers": self._next_action,
            "Fist": self._stop_previous,
        }
        pyautogui.FAILSAFE = False
        print(f"[ActionController] Initialized (cooldown={cooldown_time}s)")

    def _init_volume(self):
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume_interface = cast(
                interface, POINTER(IAudioEndpointVolume))
        except Exception:
            self.volume_interface = None

    def execute(self, gesture):
        if gesture.name == "Unknown" or gesture.name not in self.action_map:
            return False
        if not self._cooldown_passed(gesture.name):
            return False

        self.action_map[gesture.name]()
        self.last_action_time[gesture.name] = time.time()
        self.last_gesture = gesture.name
        return True

    def _cooldown_passed(self, name):
        if name not in self.last_action_time:
            return True
        return (time.time() - self.last_action_time[name]) >= self.cooldown_time

    def _volume_up(self):
        print("[Action] Volume Up")
        if self.volume_interface:
            try:
                cur = self.volume_interface.GetMasterVolumeLevelScalar()
                self.volume_interface.SetMasterVolumeLevelScalar(
                    min(1.0, cur + 0.1), None)
                return
            except Exception:
                pass
        pyautogui.press('volumeup')

    def _volume_down(self):
        print("[Action] Volume Down")
        if self.volume_interface:
            try:
                cur = self.volume_interface.GetMasterVolumeLevelScalar()
                self.volume_interface.SetMasterVolumeLevelScalar(
                    max(0.0, cur - 0.1), None)
                return
            except Exception:
                pass
        pyautogui.press('volumedown')

    def _play_pause(self):
        print("[Action] Play/Pause")
        pyautogui.press('playpause')

    def _next_action(self):
        print("[Action] Next")
        pyautogui.press('nexttrack')

    def _stop_previous(self):
        print("[Action] Previous/Stop")
        pyautogui.press('prevtrack')

    def get_cooldown_remaining(self, name):
        if name not in self.last_action_time:
            return 0.0
        return round(max(0.0, self.cooldown_time -
                         (time.time() - self.last_action_time[name])), 1)
