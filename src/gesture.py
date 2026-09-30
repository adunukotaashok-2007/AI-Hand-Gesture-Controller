"""
Gesture Data Class
Holds information about a detected gesture.
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Gesture:
    name: str
    action: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    finger_states: list = field(default_factory=list)

    def __str__(self):
        return (f"Gesture: {self.name} | Action: {self.action} | "
                f"Time: {self.timestamp.strftime('%H:%M:%S')}")

    def to_dict(self):
        return {
            "name": self.name,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "confidence": self.confidence,
            "finger_states": str(self.finger_states)
        }
