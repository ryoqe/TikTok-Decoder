import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui_app import launch_gui

if __name__ == "__main__":
    launch_gui()
