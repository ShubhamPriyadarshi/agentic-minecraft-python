# Minecraft Python Edition

A fully-featured 3D voxel sandbox game built entirely in Python using Pygame and OpenGL. Explore procedurally generated worlds, mine blocks, build structures, and survive in an infinite world.

## Features

- **Procedural World Generation** - Infinite terrain with biomes, caves, ores, and trees
- **Multiple Biomes** - Plains, forests, deserts, mountains, and beaches
- **Block System** - 18 different block types with unique textures
- **First-Person Controls** - Smooth WASD movement with mouse look
- **Building & Mining** - Break and place blocks with raycasting
- **Physics** - Gravity, collision detection, and jumping
- **Particle Effects** - Block breaking particles with physics
- **Day/Night Cycle** - Dynamic lighting system
- **Chunk System** - Efficient mesh generation with face culling
- **Inventory System** - 9-slot hotbar with block selection
- **HUD** - FPS counter, coordinates, controls display

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

```bash
cd minecraft
pip install -r requirements.txt
python minecraft.py
```

## Controls

| Key | Action |
|-----|--------|
| **W** | Move forward |
| **A** | Move left |
| **S** | Move backward |
| **D** | Move right |
| **Mouse** | Look around |
| **Space** | Jump |
| **Left Shift** | Sprint |
| **Left Click** | Break block |
| **Right Click** | Place block |
| **1-9** | Select block type |
| **Scroll Wheel** | Cycle block types |
| **R** | Regenerate world |
| **ESC** | Pause/Resume |

## Project Structure

```
minecraft/
├── minecraft.py                 # Main entry point
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── src/
    ├── __init__.py
    ├── core/
    │   ├── __init__.py
    │   └── config.py            # Game configuration
    ├── world/
    │   ├── __init__.py
    │   ├── blocks.py            # Block types and textures
    │   ├── chunk.py             # Chunk management
    │   ├── terrain.py           # Procedural generation
    │   └── world.py             # World management
    ├── rendering/
    │   ├── __init__.py
    │   ├── renderer.py          # OpenGL renderer
    │   ├── hud.py               # Heads-up display
    │   ├── shaders.py           # Shader source code
    │   └── opengl_utils.py      # OpenGL utilities
    └── game/
        ├── __init__.py
        ├── game.py              # Main game loop
        ├── player.py            # Player controller
        └── particles.py         # Particle system
```

## Architecture

### World System

- **Chunks** - 16x128x16 block sections rendered independently
- **Face Culling** - Only visible faces are rendered for performance
- **Mesh Batching** - Each chunk is a single draw call
- **Dynamic Loading** - Chunks load/unload based on player position

### Terrain Generation

- **Simplex Noise** - Procedural heightmap generation
- **Biome System** - Temperature and moisture determine biome type
- **Ore Distribution** - Coal, iron, gold, and diamond ores at various depths
- **Cave Systems** - 3D noise-based cave generation
- **Tree Generation** - Automatic tree placement based on biome

### Rendering Pipeline

1. **Skybox** - Large cube with gradient sky
2. **World Rendering** - Chunk meshes with lighting
3. **Block Highlight** - Wireframe outline on targeted block
4. **Particles** - Block breaking effects
5. **HUD** - 2D overlay with game information

### Block Types

| Block | Color | Notes |
|-------|-------|-------|
| Grass | Green | Surface block in plains/forests |
| Dirt | Brown | Under grass layers |
| Stone | Gray | Main underground material |
| Wood | Dark brown | Tree trunks |
| Leaves | Dark green | Tree foliage |
| Sand | Yellow | Beaches and deserts |
| Water | Blue | Oceans and lakes |
| Cobblestone | Gray | Mountain biomes |
| Planks | Tan | Crafted building material |
| Coal Ore | Black specks | Deep underground |
| Iron Ore | Tan specks | Deep underground |
| Gold Ore | Yellow specks | Very deep |
| Diamond Ore | Cyan specks | Deepest layers |
| Bedrock | Dark gray | Unbreakable bottom layer |
| Snow | White | High mountain peaks |
| Glass | Light blue | Transparent building block |
| Brick | Red | Crafted building block |

## Technical Details

### Performance Optimizations

- **Mesh Generation** - Only exposed faces are rendered (face culling)
- **Chunk-Based Rendering** - Only nearby chunks are loaded and rendered
- **Batched Drawing** - Each chunk is a single draw call
- **LOD System** - Distant chunks are less detailed

### Physics

- **Gravity** - Realistic gravity simulation
- **Collision Detection** - AABB collision with blocks
- **Jumping** - Variable height based on hold time
- **Sprinting** - Faster movement with shift

### World Seeds

Each world is generated with a random seed. Press **R** to generate a new world with a different seed. The current seed is 42 by default.

## Troubleshooting

### Performance Issues

- Reduce `CHUNK_LOAD_DISTANCE` in `config.py`
- Lower `TARGET_FPS` for less CPU usage
- Reduce `CHUNK_HEIGHT` for less memory usage

### Display Issues

- Ensure OpenGL 3.3+ is supported
- Update graphics drivers
- Check that PyOpenGL is properly installed

### Audio Issues

- Audio errors can be ignored in headless environments
- Install `pip install pygame` for full audio support

## Future Enhancements

- [ ] Multiplayer support
- [ ] Crafting system
- [ ] Mobs and creatures
- [ ] Day/night cycle with monsters
- [ ] Redstone-like circuitry
- [ ] Water physics
- [ ] More biomes and structures
- [ ] World saving/loading
- [ ] Sound effects
- [ ] Achievement system

## License

This project is open source and available for educational purposes.

## Acknowledgments

Inspired by Minecraft by Mojang Studios. Built with:
- [Pygame](https://www.pygame.org/) - Game framework
- [PyOpenGL](https://pyopengl.sourceforge.net/) - OpenGL bindings
- [NumPy](https://numpy.org/) - Numerical computing
