"""
Gesture Module
==============
Contains the Gesture class - a simple data class that holds
information about a detected gesture.

Why this is a separate class:
- Clean way to pass gesture data between modules
- Instead of passing multiple variables, we pass one Gesture object
- Easy to add more properties later (like confidence score)
- Demonstrates OOP concept: Encapsulation
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Gesture:
    """
    Represents a detected hand gesture.

    Attributes:
        name (str): Name of the gesture (e.g., "Thumbs Up", "Open Palm")
        action (str): What action this gesture triggers (e.g., "Volume Up")
        timestamp (datetime): When the gesture was detected
        confidence (float): How confident we are in the detection (0.0 to 1.0)
        finger_states (list): Which fingers are up [thumb, index, middle, ring, pinky]

    Why use @dataclass?
    - Automatically creates __init__, __repr__, __eq__ methods
    - Less boilerplate code
    - Perfect for classes that mainly hold data
    """

    name: str
    action: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    finger_states: list = field(default_factory=list)

    def __str__(self):
        """Human-readable string representation of the gesture."""
        return f"Gesture: {self.name} | Action: {self.action} | Time: {self.timestamp.strftime('%H:%M:%S')}"

    def to_dict(self):
        """
        Convert gesture to dictionary for database storage.

        Returns:
            dict: Gesture data as a dictionary
        """
        return {
            "name": self.name,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "finger_states": str(self.finger_states)
        }
