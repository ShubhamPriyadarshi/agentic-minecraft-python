"""Chunk system for managing and rendering voxel chunks."""

import numpy as np
from typing import Optional, Dict, Tuple, List
from src.world.blocks import BlockType, BLOCK_DATA, get_block_color


class Chunk:
    """A single chunk of the world (16xHx16 blocks)."""
    
    __slots__ = ['x', 'z', 'height', 'data', 'mesh_dirty', 'vertices', 'colors',
                 'textures', 'has_mesh', 'vao', 'vbo', 'ibo', 'index_count']
    
    def __init__(self, x: int, z: int, height: int = 128):
        self.x = x
        self.z = z
        self.height = height
        self.data = np.zeros((16, height, 16), dtype=np.uint8)
        self.mesh_dirty = True
        self.vertices: np.ndarray = np.empty((0, 3), dtype=np.float32)
        self.colors: np.ndarray = np.empty((0, 3), dtype=np.float32)
        self.textures: Dict[int, any] = {}
        self.has_mesh = False
        self.vao = 0
        self.vbo = 0
        self.ibo = 0
        self.index_count = 0
    
    def get_block(self, lx: int, ly: int, lz: int) -> int:
        """Get block at local coordinates."""
        if 0 <= lx < 16 and 0 <= ly < self.height and 0 <= lz < 16:
            return self.data[lx, ly, lz]
        return BlockType.AIR.value
    
    def set_block(self, lx: int, ly: int, lz: int, block: int):
        """Set block at local coordinates."""
        if 0 <= lx < 16 and 0 <= ly < self.height and 0 <= lz < 16:
            self.data[lx, ly, lz] = block
            self.mesh_dirty = True
    
    def is_solid(self, lx: int, ly: int, lz: int) -> bool:
        """Check if block at position is solid."""
        block = self.get_block(lx, ly, lz)
        if block == BlockType.AIR.value:
            return False
        return BLOCK_DATA.get(BlockType(block), {}).get("solid", False)
    
    def rebuild_mesh(self, textures: Dict):
        """Rebuild the chunk mesh using face culling."""
        vertices = []
        indices = []
        vertex_offset = 0
        
        # Face directions: (dx, dy, dz, face_index)
        # face_index: 0=+Y top, 1=-Y bottom, 2=+X right, 3=-X left, 4=+Z front, 5=-Z back
        faces = [
            (0, 1, 0, 0,  [0,1,0, 0,1,1, 1,1,1, 1,1,0]),   # Top (+Y)
            (0, -1, 0, 1,  [0,0,0, 0,0,1, 1,0,1, 1,0,0]),   # Bottom (-Y)
            (1, 0, 0, 2,  [1,0,0, 1,1,0, 1,1,1, 1,0,1]),   # Right (+X)
            (-1, 0, 0, 3,  [0,0,0, 0,1,0, 0,1,1, 0,0,1]),   # Left (-X)
            (0, 0, 1, 4,  [0,0,1, 0,1,1, 1,1,1, 1,0,1]),   # Front (+Z)
            (0, 0, -1, 5,  [1,0,0, 1,1,0, 0,1,0, 0,0,0]),   # Back (-Z)
        ]
        
        chunk_world_x = self.x * 16
        chunk_world_z = self.z * 16
        
        for lx in range(16):
            for ly in range(self.height):
                for lz in range(16):
                    block = self.data[lx, ly, lz]
                    if block == BlockType.AIR.value:
                        continue
                    
                    block_type = BlockType(block)
                    block_info = BLOCK_DATA.get(block_type, {})
                    
                    if block_info.get("hardness", 0) == -1:
                        continue
                    
                    for dx, dy, dz, face_idx, corners in faces:
                        nx, ny, nz = lx + dx, ly + dy, lz + dz
                        
                        # Check if neighbor is transparent (needs face)
                        neighbor_block = self.get_block(nx, ny, nz)
                        
                        # If neighbor is air or transparent, show face
                        if neighbor_block == BlockType.AIR.value:
                            self._add_face(vertices, indices, 
                                         lx, ly, lz, dx, dy, dz, 
                                         face_idx, block, vertex_offset, corners)
                            vertex_offset += 4
                        elif neighbor_block != block:
                            neighbor_type = BlockType(neighbor_block)
                            neighbor_info = BLOCK_DATA.get(neighbor_type, {})
                            if neighbor_info.get("transparent", False):
                                self._add_face(vertices, indices,
                                             lx, ly, lz, dx, dy, dz,
                                             face_idx, block, vertex_offset, corners)
                                vertex_offset += 4
        
        if vertices:
            # Split into position and color arrays for ES2 compatibility
            arr = np.array(vertices, dtype=np.float32)
            self.vertices = arr[:, :3]  # x, y, z
            self.colors = arr[:, 3:6]   # r, g, b
            self.index_count = len(indices)
            self.has_mesh = True
        else:
            self.vertices = np.empty((0, 3), dtype=np.float32)
            self.colors = np.empty((0, 3), dtype=np.float32)
            self.index_count = 0
            self.has_mesh = False
        
        self.mesh_dirty = False
    
    def _add_face(self, vertices: list, indices: list,
                  lx: int, ly: int, lz: int, dx: int, dy: int, dz: int,
                  face_idx: int, block: int, offset: int, corners: tuple):
        """Add a single face to the vertex/index arrays."""
        base_x = self.x * 16 + lx
        base_y = ly
        base_z = self.z * 16 + lz
        
        # Lighting values per face
        colors = {
            0: (1.0, 1.0, 1.0),      # Top - bright
            1: (0.5, 0.5, 0.5),      # Bottom - dark
            2: (0.8, 0.8, 0.8),      # Right
            3: (0.7, 0.7, 0.7),      # Left
            4: (0.9, 0.9, 0.9),      # Front
            5: (0.75, 0.75, 0.75),   # Back
        }
        
        color = colors.get(face_idx, (0.8, 0.8, 0.8))
        
        # Corner positions for this face
        corner_positions = [
            (base_x + corners[0], base_y + corners[1], base_z + corners[2]),
            (base_x + corners[3], base_y + corners[4], base_z + corners[5]),
            (base_x + corners[6], base_y + corners[7], base_z + corners[8]),
            (base_x + corners[9], base_y + corners[10], base_z + corners[11]),
        ]
        
        # UV coordinates for this face
        uvs = [(0, 0), (0, 1), (1, 1), (1, 0)]
        
        for i, (cx, cy, cz) in enumerate(corner_positions):
            u, v = uvs[i]
            # x, y, z, r, g, b, u, v
            vertices.append([cx, cy, cz, 
                           color[0], color[1], color[2],
                           u, v])
        
        # Two triangles per face
        indices.extend([offset, offset + 1, offset + 2])
        indices.extend([offset, offset + 2, offset + 3])
