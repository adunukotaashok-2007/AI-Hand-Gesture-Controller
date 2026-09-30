"""
Test Module for GestureRecognizer
=================================
Unit tests to verify gesture recognition works correctly.

These tests can be run without a camera - they test the logic only.

Why test?
- Verify each gesture pattern is recognized correctly
- Catch bugs early
- Show during presentation that we tested our code
- Professional development practice

Run with: python -m pytest tests/ -v
Or simply: python tests/test_gesture_recognizer.py
"""

import sys
import os

# Add parent directory to path so we can import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gesture_recognizer import GestureRecognizer


def test_thumbs_up():
    """Test that [1,0,0,0,0] is recognized as Thumbs Up."""
    recognizer = GestureRecognizer()
    gesture = recognizer.recognize([1, 0, 0, 0, 0])
    assert gesture.name == "Thumbs Up", \
        f"Expected 'Thumbs Up', got '{gesture.name}'"
    assert gesture.action == "Volume Up"
    print("✅ Thumbs Up test passed")


def test_open_palm():
    """Test that [1,1,1,1,1] is recognized as Open Palm."""
    recognizer = GestureRecognizer()
    gesture = recognizer.recognize([1, 1, 1, 1, 1])
    assert gesture.name == "Open Palm", \
        f"Expected 'Open Palm', got '{gesture.name}'"
    assert gesture.action == "Play/Pause"
    print("✅ Open Palm test passed")


def test_two_fingers():
    """Test that [0,1,1,0,0] is recognized as Two Fingers."""
    recognizer = GestureRecognizer()
    gesture = recognizer.recognize([0, 1, 1, 0, 0])
    assert gesture.name == "Two Fingers", \
        f"Expected 'Two Fingers', got '{gesture.name}'"
    assert gesture.action == "Next"
    print("✅ Two Fingers test passed")


def test_fist():
    """Test that [0,0,0,0,0] without thumb-down landmarks is Fist."""
    recognizer = GestureRecognizer()
    # Without landmark_list, fist detection (not thumbs down)
    gesture = recognizer.recognize([0, 0, 0, 0, 0])
    assert gesture.name == "Fist", \
        f"Expected 'Fist', got '{gesture.name}'"
    assert gesture.action == "Stop/Previous"
    print("✅ Fist test passed")


def test_unknown_gesture():
    """Test that unrecognized patterns return Unknown."""
    recognizer = GestureRecognizer()
    # Random finger pattern that isn't mapped
    gesture = recognizer.recognize([1, 1, 0, 0, 0])
    assert gesture.name == "Unknown", \
        f"Expected 'Unknown', got '{gesture.name}'"
    print("✅ Unknown gesture test passed")


def test_empty_input():
    """Test that empty input returns Unknown."""
    recognizer = GestureRecognizer()
    gesture = recognizer.recognize([])
    assert gesture.name == "Unknown"
    print("✅ Empty input test passed")


def test_invalid_input():
    """Test that wrong-length input returns Unknown."""
    recognizer = GestureRecognizer()
    gesture = recognizer.recognize([1, 1])
    assert gesture.name == "Unknown"
    print("✅ Invalid input test passed")


def test_all_gestures_have_actions():
    """Test that every mapped gesture has a non-empty action."""
    recognizer = GestureRecognizer()
    all_gestures = recognizer.get_all_gestures()
    for g in all_gestures:
        assert g["action"] != "", f"Gesture {g['name']} has no action"
    print("✅ All gestures have actions test passed")


if __name__ == "__main__":
    print("\n--- Running Gesture Recognizer Tests ---\n")
    test_thumbs_up()
    test_open_palm()
    test_two_fingers()
    test_fist()
    test_unknown_gesture()
    test_empty_input()
    test_invalid_input()
    test_all_gestures_have_actions()
    print("\n--- All Tests Passed! ---\n")
