"""Player controller with movement, physics, and interaction."""

import numpy as np
import pygame
from src.core.config import (PLAYER_SPEED, PLAYER_SPRINT_SPEED, PLAYER_JUMP_FORCE,
                             PLAYER_GRAVITY, PLAYER_HEIGHT, PLAYER_WIDTH,
                             MOUSE_SENSITIVITY, BLOCK_REACH)
from src.world.blocks import BlockType


class Player:
    """First-person player with WASD movement, mouse look, and block interaction."""
    
    def __init__(self, world, x: float = 0.0, y: float = 70.0, z: float = 0.0):
        self.world = world
        self.position = np.array([x, y, z], dtype=np.float32)
        self.velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.rotation = np.array([0.0, 0.0], dtype=np.float32)  # pitch, yaw
        
        self.on_ground = False
        self.sprinting = False
        self.selected_slot = 0
        
        # Key state
        self.keys = {}
        
        # Find spawn point
        self._find_spawn()
    
    def _find_spawn(self):
        """Find a safe spawn point."""
        for y in range(120, 0, -1):
            if self.world.get_block(int(self.position[0]), y, int(self.position[2])) == BlockType.AIR.value:
                self.position[1] = y + 1
                break
    
    def handle_keys(self, keys):
        """Store key state."""
        self.keys = keys
    
    def handle_mouse(self, dx: float, dy: float):
        """Handle mouse movement for camera rotation."""
        self.rotation[1] += dx * MOUSE_SENSITIVITY  # yaw
        self.rotation[0] -= dy * MOUSE_SENSITIVITY  # pitch
        
        # Clamp pitch to avoid flipping
        self.rotation[0] = np.clip(self.rotation[0], -89.0, 89.0)
    
    def update(self, dt: float):
        """Update player position and physics."""
        # Calculate movement direction
        move = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        
        speed = PLAYER_SPRINT_SPEED if self.sprinting else PLAYER_SPEED
        
        yaw = np.radians(self.rotation[1])
        
        if self.keys.get(pygame.K_w, False):
            move[0] -= np.sin(yaw)
            move[2] -= np.cos(yaw)
        if self.keys.get(pygame.K_s, False):
            move[0] += np.sin(yaw)
            move[2] += np.cos(yaw)
        if self.keys.get(pygame.K_a, False):
            move[0] -= np.cos(yaw)
            move[2] += np.sin(yaw)
        if self.keys.get(pygame.K_d, False):
            move[0] += np.cos(yaw)
            move[2] -= np.sin(yaw)
        if self.keys.get(pygame.K_SPACE, False) and self.on_ground:
            self.velocity[1] = PLAYER_JUMP_FORCE
            self.on_ground = False
        if self.keys.get(pygame.K_LSHIFT, False):
            self.sprinting = True
        else:
            self.sprinting = False
        
        # Normalize movement
        if np.linalg.norm(move) > 0:
            move = move / np.linalg.norm(move)
        
        # Apply movement
        self.velocity[0] = move[0] * speed
        self.velocity[2] = move[2] * speed
        
        # Apply gravity
        self.velocity[1] += PLAYER_GRAVITY * dt
        
        # Collision detection and response
        self._collide_and_move(dt)
    
    def _collide_and_move(self, dt: float):
        """Handle collision detection and response."""
        world = self.world
        
        # Try moving X
        new_x = self.position[0] + self.velocity[0] * dt
        if not self._collides(new_x, self.position[1], self.position[2]):
            self.position[0] = new_x
        else:
            self.velocity[0] = 0
        
        # Try moving Z
        new_z = self.position[2] + self.velocity[2] * dt
        if not self._collides(self.position[0], self.position[1], new_z):
            self.position[2] = new_z
        else:
            self.velocity[2] = 0
        
        # Try moving Y
        new_y = self.position[1] + self.velocity[1] * dt
        if not self._collides(self.position[0], new_y, self.position[2]):
            self.position[1] = new_y
            self.on_ground = False
        else:
            if self.velocity[1] < 0:
                self.on_ground = True
            self.velocity[1] = 0
    
    def _collides(self, x: float, y: float, z: float) -> bool:
        """Check if position collides with any solid block."""
        # Check player bounding box
        width = PLAYER_WIDTH
        
        # Check feet and head
        for dy in [0, PLAYER_HEIGHT - 0.1]:
            for dx in [-width, width]:
                for dz in [-width, width]:
                    bx, by, bz = int(x + dx), int(y + dy), int(z + dz)
                    block = self.world.get_block(bx, by, bz)
                    if block != BlockType.AIR.value:
                        block_type = BlockType(block)
                        from src.world.blocks import BLOCK_DATA
                        if BLOCK_DATA.get(block_type, {}).get("solid", False):
                            return True
        
        return False
    
    def get_look_vector(self) -> np.ndarray:
        """Get the direction the player is looking."""
        pitch = np.radians(self.rotation[0])
        yaw = np.radians(self.rotation[1])
        
        x = -np.sin(yaw) * np.cos(pitch)
        y = np.sin(pitch)
        z = -np.cos(yaw) * np.cos(pitch)
        
        return np.array([x, y, z], dtype=np.float32)
    
    def get_position(self) -> np.ndarray:
        """Get player position."""
        return self.position.copy()
    
    def get_rotation(self) -> np.ndarray:
        """Get player rotation."""
        return self.rotation.copy()
    
    def raycast(self, max_dist: float = BLOCK_REACH) -> tuple:
        """Raycast from player's view to find targeted block.
        
        Returns:
            (hit_x, hit_y, hit_z, block_x, block_y, block_z) or None if nothing hit
            where (hit_*) are the hit position and (block_*) is the broken block position
        """
        start = self.position.copy()
        direction = self.get_look_vector()
        
        step = 0.05
        prev_x, prev_y, prev_z = int(start[0]), int(start[1]), int(start[2])
        
        for dist in np.arange(0, max_dist, step):
            x = start[0] + direction[0] * dist
            y = start[1] + direction[1] * dist
            z = start[2] + direction[2] * dist
            
            bx, by, bz = int(x), int(y), int(z)
            
            block = self.world.get_block(bx, by, bz)
            
            if block != BlockType.AIR.value and block != BlockType.WATER.value:
                return (prev_x, prev_y, prev_z, bx, by, bz)
            
            prev_x, prev_y, prev_z = bx, by, bz
        
        return None
    
    def break_block(self, x: int, y: int, z: int):
        """Break a block at the given position."""
        self.world.set_block(x, y, z, BlockType.AIR.value)
    
    def place_block(self, x: int, y: int, z: int, block_type: int):
        """Place a block at the given position."""
        # Don't place block inside player
        px, py, pz = self.position[0], self.position[1], self.position[2]
        if (x - 1 <= int(px) <= x + 1 and 
            y <= int(py) + 1 <= y + 1 and 
            z - 1 <= int(pz) <= z + 1):
            return
        
        self.world.set_block(x, y, z, block_type)
