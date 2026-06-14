#!/usr/bin/env python3
"""
Minecraft Python Edition
A 3D voxel game built with Python, Pygame, and OpenGL.

Controls:
    WASD      - Move
    Mouse     - Look around
    Space     - Jump
    Shift     - Sprint
    Left Click - Break block
    Right Click - Place block
    1-9       - Select block type
    Scroll    - Cycle block types
    R         - Regenerate world
    ESC       - Pause/Resume
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.game.game import Game


def main():
    """Entry point for the Minecraft game."""
    print("Starting Minecraft Python Edition...")
    print("Loading world...")
    
    game = Game()
    game.run()
    
    print("Goodbye!")


if __name__ == "__main__":
    main()
