"""Software renderer for macOS Apple Silicon (no OpenGL support).

Uses pygame's built-in 2D capabilities with numpy array blitting
for fast 3D rendering without OpenGL.
"""

import pygame
import numpy as np
import math
from pygame.locals import DOUBLEBUF, RESIZABLE
from src.core.config import WINDOW_WIDTH, WINDOW_HEIGHT, FOG_NEAR, FOG_FAR


class SoftwareRenderer:
    """Software-based renderer that works on macOS Apple Silicon."""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        self.width = width
        self.height = height
        self.fog_near = FOG_NEAR
        self.fog_far = FOG_FAR
        
        pygame.init()
        self.screen = pygame.display.set_mode(
            (width, height), DOUBLEBUF | RESIZABLE
        )
        pygame.display.set_caption("Minecraft Python Edition")
        
        # Sky color as RGB array
        self.sky_color = np.array([135, 186, 250], dtype=np.uint8)
        
        # Frame buffer as RGB array (H, W, 3)
        self.frame_buffer = np.zeros((height, width, 3), dtype=np.uint8)
        # Depth buffer (H, W) - store inverse depth for sorting
        self.depth_buffer = np.full((height, width), 0.0, dtype=np.float32)
        
    def clear(self):
        """Clear the screen."""
        self.frame_buffer[:] = self.sky_color
        self.depth_buffer[:] = 0.0
        
    def resize(self, width: int, height: int):
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode(
            (width, height), DOUBLEBUF | RESIZABLE
        )
        self.frame_buffer = np.zeros((height, width, 3), dtype=np.uint8)
        self.depth_buffer = np.full((height, width), 0.0, dtype=np.float32)
        
    def setup_camera(self, pos, target):
        self.camera_pos = pos
        return np.eye(4, dtype=np.float32)
        
    def setup_projection(self, fov=70.0):
        return np.eye(4, dtype=np.float32)
        
    def render_chunk(self, vertices, colors, indices):
        """Render a chunk using optimized numpy-based rendering."""
        h, w = self.height, self.width
        fov_rad = math.radians(70.0)
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        # Get camera position and rotation
        if hasattr(self, 'camera_pos'):
            cam_x, cam_y, cam_z = self.camera_pos[0], self.camera_pos[1], self.camera_pos[2]
        else:
            cam_x, cam_y, cam_z = 0, 70, 0
        yaw = self.rotation[1] if hasattr(self, 'rotation') else 0
        pitch = self.rotation[0] if hasattr(self, 'rotation') else 0
        
        # Transform all vertices once
        transformed = []
        for v in vertices:
            dx, dy, dz = v[0] - cam_x, v[1] - cam_y, v[2] - cam_z
            cos_y, sin_y = math.cos(yaw), math.sin(yaw)
            rx = dx * cos_y - dz * sin_y
            rz = dx * sin_y + dz * cos_y
            cos_p, sin_p = math.cos(pitch), math.sin(pitch)
            ry = dy * cos_p - rz * sin_p
            rz2 = dy * sin_p + rz * cos_p
            if rz2 > 0.1:
                sx = w/2 + (rx / rz2) * f * w/2
                sy = h/2 - (ry / rz2) * f * h/2
                transformed.append((sx, sy, rz2))
            else:
                transformed.append((w/2, h/2, 0.1))
        
        # Sort triangles by average depth (painter's algorithm)
        triangles = []
        for i in range(0, len(indices), 3):
            v0 = transformed[indices[i]]
            v1 = transformed[indices[i+1]]
            v2 = transformed[indices[i+2]]
            
            # Backface culling
            edge1x = v1[0] - v0[0]
            edge1y = v1[1] - v0[1]
            edge2x = v2[0] - v0[0]
            edge2y = v2[1] - v0[1]
            cross = edge1x * edge2y - edge1y * edge2x
            if cross < 0:
                continue
            if v0[2] < 0.1 or v1[2] < 0.1 or v2[2] < 0.1:
                continue
                
            avg_depth = (v0[2] + v1[2] + v2[2]) / 3.0
            triangles.append((avg_depth, v0, v1, v2, indices[i], indices[i+1], indices[i+2]))
        
        # Sort by depth (far to near)
        triangles.sort(key=lambda t: t[0], reverse=True)
        
        # Render each triangle
        for tri in triangles:
            depth, v0, v1, v2, idx0, idx1, idx2 = tri
            
            x_min = max(0, min(int(v0[0]), int(v1[0]), int(v2[0])))
            x_max = min(w-1, max(int(v0[0]), int(v1[0]), int(v2[0])))
            y_min = max(0, min(int(v0[1]), int(v1[1]), int(v2[1])))
            y_max = min(h-1, max(int(v0[1]), int(v1[1]), int(v2[1])))
            
            if x_min > x_max or y_min > y_max:
                continue
                
            c0 = colors[idx0] * 255
            c1 = colors[idx1] * 255
            c2 = colors[idx2] * 255
            
            fog_factor = min(1.0, max(0.0, (depth - self.fog_near) / (self.fog_far - self.fog_near)))
            fog = np.array([85, 155, 186], dtype=np.uint8)
            
            # Simple filled triangle using barycentric coordinates
            self._draw_triangle(x_min, x_max, y_min, y_max, v0, v1, v2, c0, c1, c2, fog, fog_factor, float(depth))
            
    def _draw_triangle(self, x_min, x_max, y_min, y_max, v0, v1, v2, c0, c1, c2, fog_color, fog_factor, depth):
        """Draw a single triangle using barycentric coordinates."""
        ex1 = v1[0] - v0[0]
        ey1 = v1[1] - v0[1]
        ex2 = v2[0] - v0[0]
        ey2 = v2[1] - v0[1]
        area = ex1 * ey2 - ex2 * ey1
        
        if abs(area) < 1e-10:
            return
        
        fb = self.frame_buffer
        db = self.depth_buffer
        
        for y in range(y_min, y_max + 1):
            if y < 0 or y >= self.height:
                continue
            for x in range(x_min, x_max + 1):
                if x < 0 or x >= self.width:
                    continue
                dx0 = x - v0[0]
                dy0 = y - v0[1]
                dx1 = x - v1[0]
                dy1 = y - v1[1]
                dx2 = x - v2[0]
                dy2 = y - v2[1]
                
                alpha = (dx1 * dy2 - dx2 * dy1) / area
                beta = (dx2 * dy0 - dx0 * dy2) / area
                gamma = 1.0 - alpha - beta
                
                if alpha > -0.01 and beta > -0.01 and gamma > -0.01:
                    if depth < db[y, x]:
                        db[y, x] = depth
                        r = alpha * c0[0] + beta * c1[0] + gamma * c2[0]
                        g = alpha * c0[1] + beta * c1[1] + gamma * c2[1]
                        b = alpha * c0[2] + beta * c1[2] + gamma * c2[2]
                        fb[y, x] = np.array([
                            max(0, min(255, int(r * (1 - fog_factor * 0.3) + fog_color[0] * fog_factor * 0.3))),
                            max(0, min(255, int(g * (1 - fog_factor * 0.3) + fog_color[1] * fog_factor * 0.3))),
                            max(0, min(255, int(b * (1 - fog_factor * 0.3) + fog_color[2] * fog_factor * 0.3)))
                        ], dtype=np.uint8)
                        
    def draw_block_outline(self, x, y, z, color=(255, 255, 255)):
        pass
        
    def update(self):
        """Update the display."""
        surf = pygame.surfarray.make_surface(self.frame_buffer.swapaxes(0, 1))
        self.screen.blit(surf, (0, 0))
        pygame.display.flip()
        
    def handle_events(self):
        """Handle pygame events."""
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
