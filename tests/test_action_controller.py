"""
Tests for ActionController - Cooldown and action mapping.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.action_controller import ActionController
from src.gesture import Gesture


def test_cooldown_blocks_repeat():
    """Same gesture should NOT trigger twice within cooldown."""
    controller = ActionController(cooldown_time=1.0)
    gesture = Gesture(name="Thumbs Up", action="Volume Up")

    result1 = controller.execute(gesture)
    assert result1 is True, "First time should work"

    result2 = controller.execute(gesture)
    assert result2 is False, "Second time should be blocked"

    print("  Cooldown blocking: PASS")


def test_cooldown_allows_after_wait():
    """Gesture should work again after cooldown passes."""
    controller = ActionController(cooldown_time=0.5)
    gesture = Gesture(name="Open Palm", action="Play/Pause")

    controller.execute(gesture)
    time.sleep(0.6)

    result = controller.execute(gesture)
    assert result is True, "Should work after cooldown"

    print("  Cooldown after wait: PASS")


def test_different_gestures_independent():
    """Different gestures should have separate cooldowns."""
    controller = ActionController(cooldown_time=1.0)
    g1 = Gesture(name="Thumbs Up", action="Volume Up")
    g2 = Gesture(name="Open Palm", action="Play/Pause")

    controller.execute(g1)

    result = controller.execute(g2)
    assert result is True, "Different gesture should not be blocked"

    print("  Independent cooldowns: PASS")


def test_unknown_not_executed():
    """Unknown gestures should be ignored."""
    controller = ActionController(cooldown_time=1.0)
    gesture = Gesture(name="Unknown", action="None")

    result = controller.execute(gesture)
    assert result is False, "Unknown should not execute"

    print("  Unknown rejection: PASS")


def test_cooldown_remaining():
    """Cooldown timer should show remaining seconds."""
    controller = ActionController(cooldown_time=2.0)
    gesture = Gesture(name="Fist", action="Stop/Previous")

    controller.execute(gesture)
    remaining = controller.get_cooldown_remaining("Fist")

    assert remaining > 0, "Should have time remaining"
    assert remaining <= 2.0, "Should not exceed cooldown"

    print("  Cooldown timer: PASS")


if __name__ == "__main__":
    print("\n--- Action Controller Tests ---")
    test_cooldown_blocks_repeat()
    test_cooldown_allows_after_wait()
    test_different_gestures_independent()
    test_unknown_not_executed()
    test_cooldown_remaining()
    print("--- All Tests Passed! ---\n")
