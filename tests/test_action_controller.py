"""
Test Module for ActionController
=================================
Tests cooldown mechanism and action mapping.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.action_controller import ActionController
from src.gesture import Gesture


def test_cooldown_blocks_rapid_actions():
    """Test that the same gesture can't trigger twice within cooldown."""
    controller = ActionController(cooldown_time=1.0)
    gesture = Gesture(name="Thumbs Up", action="Volume Up")

    # First execution should succeed
    result1 = controller.execute(gesture)
    assert result1 is True, "First execution should succeed"

    # Immediate second execution should be blocked
    result2 = controller.execute(gesture)
    assert result2 is False, "Second execution should be blocked by cooldown"

    print("✅ Cooldown blocking test passed")


def test_cooldown_allows_after_wait():
    """Test that action is allowed after cooldown period."""
    controller = ActionController(cooldown_time=0.5)
    gesture = Gesture(name="Open Palm", action="Play/Pause")

    controller.execute(gesture)

    # Wait for cooldown to pass
    time.sleep(0.6)

    result = controller.execute(gesture)
    assert result is True, "Should be allowed after cooldown"

    print("✅ Cooldown allow after wait test passed")


def test_different_gestures_independent_cooldown():
    """Test that different gestures have independent cooldowns."""
    controller = ActionController(cooldown_time=1.0)
    gesture1 = Gesture(name="Thumbs Up", action="Volume Up")
    gesture2 = Gesture(name="Open Palm", action="Play/Pause")

    # Execute gesture 1
    controller.execute(gesture1)

    # Gesture 2 should still work (independent cooldown)
    result = controller.execute(gesture2)
    assert result is True, "Different gesture should not be affected"

    print("✅ Independent cooldown test passed")


def test_unknown_gesture_not_executed():
    """Test that unknown gestures are not executed."""
    controller = ActionController(cooldown_time=1.0)
    gesture = Gesture(name="Unknown", action="None")

    result = controller.execute(gesture)
    assert result is False, "Unknown gesture should not execute"

    print("✅ Unknown gesture rejection test passed")


if __name__ == "__main__":
    print("\n--- Running Action Controller Tests ---\n")
    test_cooldown_blocks_rapid_actions()
    test_cooldown_allows_after_wait()
    test_different_gestures_independent_cooldown()
    test_unknown_gesture_not_executed()
    print("\n--- All Tests Passed! ---\n")
