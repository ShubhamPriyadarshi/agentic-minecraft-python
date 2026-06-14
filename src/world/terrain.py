"""Procedural terrain generation using simplex noise."""

import numpy as np
from typing import Optional
from src.world.blocks import BlockType
from src.world.chunk import Chunk


class SimplexNoise:
    """Simple 2D/3D simplex noise implementation."""
    
    def __init__(self, seed: Optional[int] = None):
        self.perm = np.zeros(512, dtype=np.int32)
        grad3 = [
            [1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],
            [1,0,1],[-1,0,1],[1,0,-1],[-1,0,-1],
            [0,1,1],[0,-1,1],[0,1,-1],[0,-1,-1]
        ]
        self.grad3 = np.array(grad3, dtype=np.float32)
        
        if seed is None:
            seed = np.random.randint(0, 2**31)
        
        p = np.arange(256, dtype=np.int32)
        np.random.seed(seed)
        np.random.shuffle(p)
        self.perm[:256] = p
        self.perm[256:] = p
    
    def noise2d(self, xin: float, yin: float) -> float:
        """2D simplex noise."""
        scale = 0.008
        
        s = (xin * scale + yin * scale) * 0.5 * (np.sqrt(3.0) - 1.0)
        i = int(np.floor(xin * scale + s))
        j = int(np.floor(yin * scale + s))
        
        t = (i + j) * 0.5 * np.sqrt(3.0)
        X0 = i - t
        Y0 = j - t
        
        x0 = xin * scale - X0
        y0 = yin * scale - Y0
        
        i1, j1 = (0, 0) if x0 > y0 else (1, 1)
        
        x1 = x0 - i1 + 0.5
        y1 = y0 - j1 + 0.5
        x2 = x0 - 1.0 + 0.5
        y2 = y0 - 1.0 + 0.5
        
        ii = i & 255
        jj = j & 255
        
        gi0 = self.perm[ii + self.perm[jj]] % 12
        gi1 = self.perm[ii + i1 + self.perm[jj + j1]] % 12
        gi2 = self.perm[ii + 1 + self.perm[jj + 1]] % 12
        
        def _contrib(gi, x, y):
            t = 0.5 - x*x - y*y
            if t < 0:
                return 0.0
            t *= t
            return t * t * (self.grad3[gi][0] * x + self.grad3[gi][1] * y)
        
        n0 = _contrib(gi0, x0, y0)
        n1 = _contrib(gi1, x1, y1)
        n2 = _contrib(gi2, x2, y2)
        
        return 70.0 * (n0 + n1 + n2) / 60.0
    
    def octave_noise(self, x: float, y: float, octaves: int, 
                     persistence: float = 0.5, lacunarity: float = 2.0) -> float:
        """Generate multi-octave noise for more natural terrain."""
        total = 0.0
        frequency = 1.0
        amplitude = 1.0
        max_value = 0.0
        
        for _ in range(octaves):
            total += self.noise2d(x * frequency, y * frequency) * amplitude
            max_value += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return total / max_value


class TerrainGenerator:
    """Generates terrain for chunks using noise functions."""
    
    # Biome types based on moisture and temperature
    BIOME_DESERT = 0
    BIOME_PLAINS = 1
    BIOME_FOREST = 2
    BIOME_MOUNTAIN = 3
    BIOME_BEACH = 4
    
    def __init__(self, seed: Optional[int] = None, water_level: int = 32, 
                 max_height: int = 120):
        self.noise = SimplexNoise(seed)
        self.height_noise = SimplexNoise(seed + 100)
        self.moisture_noise = SimplexNoise(seed + 200)
        self.temperature_noise = SimplexNoise(seed + 300)
        self.cave_noise = SimplexNoise(seed + 400)
        self.tree_noise = SimplexNoise(seed + 500)
        self.water_level = water_level
        self.max_height = max_height
    
    def generate_chunk(self, chunk: Chunk):
        """Generate terrain for a single chunk with biomes."""
        chunk_x = chunk.x * 16
        chunk_z = chunk.z * 16
        
        # Determine biome for this chunk
        biome = self._get_biome(chunk_x + 8, chunk_z + 8)
        
        # Generate heightmap
        for x in range(16):
            for z in range(16):
                world_x = chunk_x + x
                world_z = chunk_z + z
                
                height = self._get_height(world_x, world_z, biome)
                height = int(np.clip(height, 1, self.max_height - 1))
                
                # Fill the column
                for y in range(chunk.height):
                    if y == 0:
                        chunk.set_block(x, y, z, BlockType.BEDROCK.value)
                    elif y < height - 4:
                        chunk.set_block(x, y, z, BlockType.STONE.value)
                    elif y < height - 2:
                        chunk.set_block(x, y, z, BlockType.DIRT.value)
                    elif y < height:
                        if biome == self.BIOME_DESERT or height <= self.water_level + 1:
                            chunk.set_block(x, y, z, BlockType.SAND.value)
                        elif biome == self.BIOME_MOUNTAIN and height > 70:
                            chunk.set_block(x, y, z, BlockType.COBBLESTONE.value)
                        elif biome == self.BIOME_PLAINS and height > 80:
                            chunk.set_block(x, y, z, BlockType.SNOW.value)
                        else:
                            chunk.set_block(x, y, z, BlockType.GRASS.value)
                    elif y <= self.water_level:
                        chunk.set_block(x, y, z, BlockType.WATER.value)
                    else:
                        chunk.set_block(x, y, z, BlockType.AIR.value)
                
                # Add ores
                if height > self.water_level + 4:
                    self._add_ores(chunk, x, height, z)
        
        # Add terrain features based on biome
        if biome == self.BIOME_FOREST:
            self._add_trees(chunk, chunk_x, chunk_z, density=0.025)
        elif biome == self.BIOME_PLAINS:
            self._add_trees(chunk, chunk_x, chunk_z, density=0.008)
        
        # Add caves
        self._add_caves(chunk)
    
    def _get_biome(self, wx: int, wz: int) -> int:
        """Determine biome at world coordinates."""
        temp = (self.temperature_noise.noise2d(wx * 0.003, wz * 0.003) + 1) / 2
        moist = (self.moisture_noise.noise2d(wx * 0.005, wz * 0.005) + 1) / 2
        height_factor = self._get_height(wx, wz) / 100.0
        
        if height_factor > 0.7:
            return self.BIOME_MOUNTAIN
        elif temp > 0.6 and moist < 0.3:
            return self.BIOME_DESERT
        elif moist > 0.6 and temp > 0.4:
            return self.BIOME_FOREST
        elif height_factor < 0.15:
            return self.BIOME_BEACH
        else:
            return self.BIOME_PLAINS
    
    def _get_height(self, world_x: int, world_z: int, biome: int = -1) -> float:
        """Get terrain height at world coordinates."""
        if biome == self.BIOME_MOUNTAIN:
            h = self.height_noise.octave_noise(world_x * 0.008, world_z * 0.008, 6, 0.5, 2.0)
            return 50 + h * 40 + 30  # Mountains are taller
        elif biome == self.BIOME_DESERT:
            h = self.height_noise.octave_noise(world_x * 0.01, world_z * 0.01, 4, 0.5, 2.0)
            return 35 + h * 10  # Flatter desert
        else:
            h = self.height_noise.octave_noise(world_x * 0.01, world_z * 0.01, 6, 0.5, 2.0)
            h2 = self.height_noise.octave_noise(world_x * 0.005, world_z * 0.005, 3, 0.6, 2.0)
            return 40 + h * 25 + h2 * 15
    
    def _add_ores(self, chunk: Chunk, lx: int, surface_y: int, lz: int):
        """Add ore veins in stone layers."""
        np.random.seed(lx * 1000 + lz * 100 + int(surface_y / 3))
        
        for _ in range(10):
            oy = np.random.randint(1, surface_y - 3)
            ore_type = np.random.randint(0, 100)
            
            if ore_type < 3:
                block = BlockType.DIAMOND_ORE.value
            elif ore_type < 10:
                block = BlockType.GOLD_ORE.value
            elif ore_type < 25:
                block = BlockType.IRON_ORE.value
            elif ore_type < 50:
                block = BlockType.COAL_ORE.value
            else:
                continue
            
            chunk.set_block(lx, oy, lz, block)
    
    def _add_trees(self, chunk: Chunk, chunk_x: int, chunk_z: int, density: float = 0.01):
        """Add trees to the chunk."""
        for x in range(16):
            for z in range(16):
                if np.random.random() > density:
                    continue
                
                surface_y = -1
                for y in range(chunk.height - 1, 0, -1):
                    if chunk.get_block(x, y, z) in (BlockType.GRASS.value, BlockType.SAND.value):
                        surface_y = y
                        break
                
                if surface_y < 5 or surface_y + 8 >= chunk.height:
                    continue
                
                self._place_tree(chunk, x, surface_y + 1, z)
    
    def _place_tree(self, chunk: Chunk, x: int, y: int, z: int):
        """Place a single tree with variation."""
        tree_height = np.random.randint(4, 7)
        
        # Trunk
        for ty in range(tree_height):
            chunk.set_block(x, y + ty, z, BlockType.WOOD.value)
        
        # Leaves with some variation
        leaf_start = y + tree_height - 2
        leaf_end = y + tree_height + 1
        
        for ly in range(leaf_start, leaf_end + 1):
            radius = 2 if ly == y + tree_height - 1 else (1 if ly == leaf_end else 2)
            
            for lx in range(-radius, radius + 1):
                for lz in range(-radius, radius + 1):
                    if abs(lx) == radius and abs(lz) == radius:
                        continue
                    
                    if ly == leaf_end and (abs(lx) > 1 or abs(lz) > 1):
                        continue
                    
                    if lx == 0 and lz == 0 and ly < y + tree_height:
                        continue
                    
                    chunk.set_block(x + lx, ly, z + lz, BlockType.LEAVES.value)
    
    def _add_caves(self, chunk: Chunk):
        """Add cave systems using 3D noise."""
        for x in range(16):
            for y in range(1, chunk.height - 1):
                for z in range(16):
                    world_x = chunk.x * 16 + x
                    world_y = y
                    world_z = chunk.z * 16 + z
                    
                    # 3D noise for cave generation
                    cave_val = self.cave_noise.noise2d(
                        world_x * 0.05, world_z * 0.05
                    ) + self.cave_noise.noise2d(
                        world_x * 0.1, world_y * 0.1
                    ) * 0.5
                    
                    if cave_val > 0.6 and y < 60:
                        # Make cave wider
                        for dx in range(-1, 2):
                            for dy in range(-1, 2):
                                for dz in range(-1, 2):
                                    nx, ny, nz = x + dx, y + dy, z + dz
                                    if 0 <= nx < 16 and 0 <= ny < chunk.height and 0 <= nz < 16:
                                        block = chunk.get_block(nx, ny, nz)
                                        if block not in (BlockType.BEDROCK.value,):
                                            chunk.set_block(nx, ny, nz, BlockType.AIR.value)
