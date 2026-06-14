"""Block types and block registry system."""

import pygame
import numpy as np
from enum import IntEnum
from typing import Dict, Tuple


class BlockType(IntEnum):
    """All block types in the game."""
    AIR = 0
    GRASS = 1
    DIRT = 2
    STONE = 3
    WOOD = 4
    LEAVES = 5
    SAND = 6
    WATER = 7
    COBBLESTONE = 8
    PLANKS = 9
    COAL_ORE = 10
    IRON_ORE = 11
    GOLD_ORE = 12
    DIAMOND_ORE = 13
    BEDROCK = 14
    SNOW = 15
    GLASS = 16
    BRICK = 17


# Block metadata: name, hardness, drop, transparency
BLOCK_DATA = {
    BlockType.AIR:       {"name": "Air",       "hardness": -1, "drop": None,     "transparent": True,  "solid": False},
    BlockType.GRASS:     {"name": "Grass",     "hardness": 0.6, "drop": BlockType.DIRT, "transparent": False, "solid": True},
    BlockType.DIRT:      {"name": "Dirt",      "hardness": 0.5, "drop": BlockType.DIRT, "transparent": False, "solid": True},
    BlockType.STONE:     {"name": "Stone",     "hardness": 1.5, "drop": BlockType.STONE, "transparent": False, "solid": True},
    BlockType.WOOD:      {"name": "Wood",      "hardness": 2.0, "drop": BlockType.WOOD, "transparent": False, "solid": True},
    BlockType.LEAVES:    {"name": "Leaves",    "hardness": 0.2, "drop": None,     "transparent": True,  "solid": True},
    BlockType.SAND:      {"name": "Sand",      "hardness": 0.5, "drop": BlockType.SAND, "transparent": False, "solid": True},
    BlockType.WATER:     {"name": "Water",     "hardness": -1, "drop": None,     "transparent": True,  "solid": False},
    BlockType.COBBLESTONE: {"name": "Cobblestone", "hardness": 2.0, "drop": BlockType.COBBLESTONE, "transparent": False, "solid": True},
    BlockType.PLANKS:    {"name": "Planks",    "hardness": 1.25, "drop": BlockType.PLANKS, "transparent": False, "solid": True},
    BlockType.COAL_ORE:  {"name": "Coal Ore",  "hardness": 3.0, "drop": BlockType.COAL_ORE, "transparent": False, "solid": True},
    BlockType.IRON_ORE:  {"name": "Iron Ore",  "hardness": 3.0, "drop": BlockType.IRON_ORE, "transparent": False, "solid": True},
    BlockType.GOLD_ORE:  {"name": "Gold Ore",  "hardness": 3.0, "drop": BlockType.GOLD_ORE, "transparent": False, "solid": True},
    BlockType.DIAMOND_ORE: {"name": "Diamond Ore", "hardness": 4.0, "drop": BlockType.DIAMOND_ORE, "transparent": False, "solid": True},
    BlockType.BEDROCK:   {"name": "Bedrock",   "hardness": -1, "drop": None,     "transparent": False, "solid": True},
    BlockType.SNOW:      {"name": "Snow",      "hardness": 0.5, "drop": BlockType.SNOW, "transparent": False, "solid": True},
    BlockType.GLASS:     {"name": "Glass",     "hardness": 0.3, "drop": None,     "transparent": True,  "solid": True},
    BlockType.BRICK:     {"name": "Brick",     "hardness": 2.0, "drop": BlockType.BRICK, "transparent": False, "solid": True},
}

# Hotbar-usable blocks (order matters for hotbar)
HOTBAR_BLOCKS = [
    BlockType.GRASS,
    BlockType.DIRT,
    BlockType.STONE,
    BlockType.COBBLESTONE,
    BlockType.PLANKS,
    BlockType.WOOD,
    BlockType.BRICK,
    BlockType.SAND,
    BlockType.SNOW,
    BlockType.GLASS,
]


def create_texture(size: int = 16) -> np.ndarray:
    """Create a basic colored texture as numpy array."""
    tex = np.zeros((size, size, 3), dtype=np.uint8)
    return tex


def generate_block_textures() -> Dict[int, Tuple[pygame.Surface, pygame.Surface]]:
    """Generate procedural textures for all block types.
    
    Returns dict mapping block_type -> (top_texture, side_texture)
    For blocks without top/bottom distinction, both surfaces use the same texture.
    """
    textures = {}
    
    # Color definitions for each block type (R, G, B)
    block_colors = {
        BlockType.GRASS:     {"top": (85, 170, 60),   "side": (120, 90, 50),   "bottom": (120, 90, 50)},
        BlockType.DIRT:      {"top": (120, 90, 50),   "side": (120, 90, 50),   "bottom": (120, 90, 50)},
        BlockType.STONE:     {"top": (128, 128, 128), "side": (128, 128, 128), "bottom": (128, 128, 128)},
        BlockType.WOOD:      {"top": (160, 130, 80),  "side": (90, 65, 40),    "bottom": (160, 130, 80)},
        BlockType.LEAVES:    {"top": (40, 120, 30),   "side": (40, 120, 30),   "bottom": (40, 120, 30)},
        BlockType.SAND:      {"top": (210, 200, 140), "side": (210, 200, 140), "bottom": (210, 200, 140)},
        BlockType.WATER:     {"top": (40, 80, 200),   "side": (40, 80, 200),   "bottom": (40, 80, 200)},
        BlockType.COBBLESTONE: {"top": (100, 100, 100), "side": (100, 100, 100), "bottom": (100, 100, 100)},
        BlockType.PLANKS:    {"top": (170, 135, 75),  "side": (170, 135, 75),  "bottom": (170, 135, 75)},
        BlockType.COAL_ORE:  {"top": (80, 80, 80),   "side": (80, 80, 80),    "bottom": (80, 80, 80)},
        BlockType.IRON_ORE:  {"top": (140, 120, 110), "side": (140, 120, 110), "bottom": (140, 120, 110)},
        BlockType.GOLD_ORE:  {"top": (200, 180, 80),  "side": (200, 180, 80),  "bottom": (200, 180, 80)},
        BlockType.DIAMOND_ORE: {"top": (80, 200, 200), "side": (80, 200, 200), "bottom": (80, 200, 200)},
        BlockType.BEDROCK:   {"top": (50, 50, 50),   "side": (50, 50, 50),    "bottom": (50, 50, 50)},
        BlockType.SNOW:      {"top": (240, 245, 255), "side": (240, 245, 255), "bottom": (240, 245, 255)},
        BlockType.GLASS:     {"top": (200, 220, 255), "side": (200, 220, 255), "bottom": (200, 220, 255)},
        BlockType.BRICK:     {"top": (160, 80, 70),   "side": (160, 80, 70),   "bottom": (160, 80, 70)},
    }
    
    for block_type, colors in block_colors.items():
        textures[block_type] = {}
        for face_name, color in colors.items():
            surface = pygame.Surface((16, 16), pygame.SRCALPHA)
            
            # Base color
            pygame.draw.rect(surface, (*color, 255), (0, 0, 16, 16))
            
            # Add noise/texture variation
            seed_val = int(block_type) * 1000 + abs(hash(face_name))
            np.random.seed(seed_val % (2**32))
            for _ in range(40):
                x = np.random.randint(0, 16)
                y = np.random.randint(0, 16)
                variation = np.random.randint(-30, 30)
                r = max(0, min(255, color[0] + variation))
                g = max(0, min(255, color[1] + variation))
                b = max(0, min(255, color[2] + variation))
                pygame.draw.rect(surface, (r, g, b, 255), (x, y, 1, 1))
            
            # Special textures for specific blocks
            if block_type == BlockType.GRASS and face_name == "top":
                # Add grass blade details
                for _ in range(8):
                    x = np.random.randint(0, 16)
                    y = np.random.randint(0, 16)
                    pygame.draw.rect(surface, (60, 150, 40), (x, y, 1, 1))
            
            elif block_type == BlockType.WOOD and face_name == "side":
                # Wood grain lines
                for y in range(0, 16, 3):
                    pygame.draw.rect(surface, (70, 50, 30), (0, y, 16, 1))
            
            elif block_type == BlockType.PLANKS:
                # Plank lines
                if face_name == "top":
                    for x in [4, 8, 12]:
                        pygame.draw.rect(surface, (140, 105, 55), (x, 0, 1, 16))
                else:
                    pygame.draw.rect(surface, (140, 105, 55), (0, 7, 16, 1))
            
            elif block_type == BlockType.BRICK:
                # Brick pattern
                for y in range(0, 16, 4):
                    pygame.draw.rect(surface, (180, 170, 150), (0, y, 16, 1))
                for row in range(0, 16, 4):
                    offset = 4 if row % 8 == 0 else 0
                    for x in range(offset, 16, 8):
                        pygame.draw.rect(surface, (180, 170, 150), (x, row, 1, 4))
            
            elif block_type in (BlockType.COAL_ORE, BlockType.IRON_ORE, 
                                BlockType.GOLD_ORE, BlockType.DIAMOND_ORE):
                # Ore specks
                speck_color = {
                    BlockType.COAL_ORE: (30, 30, 30),
                    BlockType.IRON_ORE: (200, 180, 160),
                    BlockType.GOLD_ORE: (240, 210, 80),
                    BlockType.DIAMOND_ORE: (100, 240, 240),
                }[block_type]
                for _ in range(4):
                    x = np.random.randint(2, 14)
                    y = np.random.randint(2, 14)
                    pygame.draw.rect(surface, speck_color, (x, y, 2, 2))
            
            textures[block_type][face_name] = surface
    
    return textures


def get_block_color(block_type: BlockType) -> Tuple[int, int, int]:
    """Get the base color for a block type."""
    colors = {
        BlockType.GRASS: (85, 170, 60),
        BlockType.DIRT: (120, 90, 50),
        BlockType.STONE: (128, 128, 128),
        BlockType.WOOD: (90, 65, 40),
        BlockType.LEAVES: (40, 120, 30),
        BlockType.SAND: (210, 200, 140),
        BlockType.WATER: (40, 80, 200),
        BlockType.COBBLESTONE: (100, 100, 100),
        BlockType.PLANKS: (170, 135, 75),
        BlockType.COAL_ORE: (80, 80, 80),
        BlockType.IRON_ORE: (140, 120, 110),
        BlockType.GOLD_ORE: (200, 180, 80),
        BlockType.DIAMOND_ORE: (80, 200, 200),
        BlockType.BEDROCK: (50, 50, 50),
        BlockType.SNOW: (240, 245, 255),
        BlockType.GLASS: (200, 220, 255),
        BlockType.BRICK: (160, 80, 70),
    }
    return colors.get(block_type, (128, 128, 128))
