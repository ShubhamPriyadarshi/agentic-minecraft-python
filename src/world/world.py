"""World management - handles chunks and world operations."""

import os
import json
import pickle
import numpy as np
from typing import Dict, Optional, Tuple, Set
from src.core.config import CHUNK_SIZE, CHUNK_HEIGHT, LOAD_DISTANCE, UNLOAD_DISTANCE
from src.world.chunk import Chunk
from src.world.terrain import TerrainGenerator
from src.world.blocks import BlockType


class World:
    """Manages the game world, including chunks and terrain generation."""
    
    def __init__(self, seed: Optional[int] = None, create_new: bool = True):
        self.chunks: Dict[Tuple[int, int], Chunk] = {}
        self.chunk_keys_loaded: Set[Tuple[int, int]] = set()
        self.terrain_gen = TerrainGenerator(seed=seed)
        self.chunk_keys_pending: Set[Tuple[int, int]] = set()
        self.dirty_chunks: Set[Tuple[int, int]] = set()
        
        if create_new:
            self._generate_initial_chunks()
    
    def _generate_initial_chunks(self):
        """Generate initial chunks around origin."""
        for x in range(-UNLOAD_DISTANCE, UNLOAD_DISTANCE + 1):
            for z in range(-UNLOAD_DISTANCE, UNLOAD_DISTANCE + 1):
                self._load_chunk(x, z)
    
    def get_chunk_key(self, wx: int, wz: int) -> Tuple[int, int]:
        """Get chunk coordinates from world coordinates."""
        return (wx // CHUNK_SIZE, wz // CHUNK_SIZE)
    
    def get_block(self, wx: int, wy: int, wz: int) -> int:
        """Get block at world coordinates."""
        cx, cz = self.get_chunk_key(wx, wz)
        chunk = self.chunks.get((cx, cz))
        
        if chunk is None:
            return BlockType.AIR.value
        
        lx = ((wx % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE
        lz = ((wz % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE
        
        if wy < 0 or wy >= chunk.height:
            return BlockType.AIR.value
        
        return chunk.get_block(lx, wy, lz)
    
    def set_block(self, wx: int, wy: int, wz: int, block: int):
        """Set block at world coordinates."""
        cx, cz = self.get_chunk_key(wx, wz)
        chunk = self.chunks.get((cx, cz))
        
        if chunk is None:
            return
        
        lx = ((wx % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE
        lz = ((wz % CHUNK_SIZE) + CHUNK_SIZE) % CHUNK_SIZE
        
        if wy < 0 or wy >= chunk.height:
            return
        
        chunk.set_block(lx, wy, lz, block)
        self.dirty_chunks.add((cx, cz))
        
        # Mark neighboring chunks as dirty if on edge
        if lx == 0:
            self.dirty_chunks.add((cx - 1, cz))
        if lx == CHUNK_SIZE - 1:
            self.dirty_chunks.add((cx + 1, cz))
        if lz == 0:
            self.dirty_chunks.add((cx, cz - 1))
        if lz == CHUNK_SIZE - 1:
            self.dirty_chunks.add((cx, cz + 1))
    
    def _load_chunk(self, cx: int, cz: int) -> Optional[Chunk]:
        """Load or generate a chunk."""
        key = (cx, cz)
        
        if key in self.chunks:
            return self.chunks[key]
        
        chunk = Chunk(cx, cz, CHUNK_HEIGHT)
        self.terrain_gen.generate_chunk(chunk)
        self.chunks[key] = chunk
        self.chunk_keys_loaded.add(key)
        
        return chunk
    
    def load_chunks_around(self, player_x: int, player_z: int):
        """Load chunks around the player position."""
        px = player_x // CHUNK_SIZE
        pz = player_z // CHUNK_SIZE
        
        # Load new chunks
        for x in range(-LOAD_DISTANCE, LOAD_DISTANCE + 1):
            for z in range(-LOAD_DISTANCE, LOAD_DISTANCE + 1):
                cx, cz = px + x, pz + z
                if (cx, cz) not in self.chunk_keys_loaded:
                    self._load_chunk(cx, cz)
        
        # Unload far chunks
        keys_to_remove = []
        for key in self.chunk_keys_loaded:
            dx = key[0] - px
            dz = key[1] - pz
            if abs(dx) > UNLOAD_DISTANCE + 1 or abs(dz) > UNLOAD_DISTANCE + 1:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.chunks[key]
            self.chunk_keys_loaded.discard(key)
    
    def get_chunks_to_render(self) -> list:
        """Get all chunks that need rendering."""
        chunks = []
        for key in self.chunk_keys_loaded:
            chunk = self.chunks[key]
            if chunk.mesh_dirty or not chunk.has_mesh:
                chunks.append(chunk)
        return chunks
    
    def rebuild_all_meshes(self, textures: Dict):
        """Rebuild meshes for all loaded chunks."""
        for chunk in self.chunks.values():
            chunk.rebuild_mesh(textures)
    
    def rebuild_dirty_meshes(self, textures: Dict):
        """Rebuild meshes for dirty chunks."""
        for key in list(self.dirty_chunks):
            chunk = self.chunks.get(key)
            if chunk:
                chunk.rebuild_mesh(textures)
        self.dirty_chunks.clear()
    
    def is_inside_block(self, wx: float, wy: float, wz: float) -> bool:
        """Check if position is inside a solid block."""
        block = self.get_block(int(wx), int(wy), int(wz))
        if block == BlockType.AIR.value:
            return False
        block_type = BlockType(block)
        return BLOCK_DATA.get(block_type, {}).get("solid", False)
    
    def save(self, filepath: str):
        """Save world to disk (simplified - just chunk positions)."""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Save metadata
        metadata = {
            "seed": self.terrain_gen.noise.perm[0] if len(self.terrain_gen.noise.perm) > 0 else 0,
            "chunks": list(self.chunks.keys()),
        }
        
        with open(filepath + ".meta", "wb") as f:
            pickle.dump(metadata, f)
    
    def load(self, filepath: str) -> bool:
        """Load world from disk."""
        if not os.path.exists(filepath + ".meta"):
            return False
        
        try:
            with open(filepath + ".meta", "rb") as f:
                metadata = pickle.load(f)
            
            # Regenerate terrain (simplified - in a full game you'd store block data)
            for (cx, cz) in metadata.get("chunks", []):
                self._load_chunk(cx, cz)
            
            return True
        except Exception:
            return False
