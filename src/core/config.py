"""Game configuration and constants."""

# Window settings
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Minecraft Python Edition"
FULLSCREEN = False
RESIZABLE = True

# Chunk settings
CHUNK_SIZE = 16
CHUNK_HEIGHT = 128
UNLOAD_DISTANCE = 4
LOAD_DISTANCE = 6

# World generation
WORLD_SEED = None
WATER_LEVEL = 32
SEA_LEVEL = 64
MAX_HEIGHT = 120
TREE_SPAWN_CHANCE = 0.02
CAVE_CHANCE = 0.005

# Player settings
PLAYER_SPEED = 5.0
PLAYER_SPRINT_SPEED = 8.0
PLAYER_JUMP_FORCE = 8.0
PLAYER_GRAVITY = -20.0
PLAYER_HEIGHT = 1.7
PLAYER_WIDTH = 0.3
MOUSE_SENSITIVITY = 0.15
MAX_FOV = 70.0

# Block reach distance
BLOCK_REACH = 6.0

# Fog settings
FOG_NEAR = 40.0
FOG_FAR = 120.0

# Day/night cycle (in seconds for full cycle)
DAY_CYCLE_DURATION = 600.0  # 10 minutes for full cycle

# Frame rate target
TARGET_FPS = 240

# World save
WORLD_DIR = "worlds"
WORLD_SAVE_INTERVAL = 60  # seconds
