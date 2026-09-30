"""Tests for GestureRecognizer."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gesture_recognizer import GestureRecognizer


def test_all():
    r = GestureRecognizer()

    assert r.recognize([1, 0, 0, 0, 0]).name == "Thumbs Up"
    assert r.recognize([1, 1, 1, 1, 1]).name == "Open Palm"
    assert r.recognize([0, 1, 1, 0, 0]).name == "Two Fingers"
    assert r.recognize([0, 0, 0, 0, 0]).name == "Fist"
    assert r.recognize([1, 1, 0, 0, 0]).name == "Unknown"
    assert r.recognize([]).name == "Unknown"

    print("All tests passed!")


if __name__ == "__main__":
    test_all()
