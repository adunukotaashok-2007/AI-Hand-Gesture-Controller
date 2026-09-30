"""
AI Hand Gesture Controller
==========================
Entry point for the application.
Run this file to start the hand gesture controller.

Usage:
    python main.py
"""

from src.application import Application


def main():
    """
    Main function that creates and runs the application.

    Why this exists:
    - Clean entry point (instead of putting code at module level)
    - Easy to understand where the program starts
    - Follows Python best practices with if __name__ == "__main__"
    """
    print("=" * 50)
    print("  AI Hand Gesture Controller")
    print("=" * 50)
    print("\nStarting application...")
    print("Press 'q' to quit the application.\n")

    # Create the application object and run it
    # All initialization happens inside the Application class
    app = Application()
    app.run()


if __name__ == "__main__":
    main()
