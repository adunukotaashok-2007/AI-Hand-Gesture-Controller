"""
AI Hand Gesture Controller - Entry Point
Run: python main.py
"""

from src.application import Application


def main():
    print("=" * 50)
    print("  AI Hand Gesture Controller")
    print("=" * 50)
    print("\nStarting application...")
    print("Press 'q' to quit the application.\n")

    app = Application()
    app.run()


if __name__ == "__main__":
    main()
