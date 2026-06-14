"""Software renderer for macOS Apple Silicon (no OpenGL support).

Uses pygame's built-in 2D capabilities to render a 3D-like view
using simple software rasterization.
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
        
        self.depth_buffer = np.full((height, width), np.finfo(np.float32).max, dtype=np.float32)
        self.sky_color = (135, 186, 250)
        
    def clear(self):
        self.screen.fill(self.sky_color)
        self.depth_buffer[:] = np.finfo(np.float32).max
        
    def setup_camera(self, pos, target):
        return np.eye(4, dtype=np.float32)
        
    def setup_projection(self, fov=70.0):
        return np.eye(4, dtype=np.float32)
        
    def render_chunk(self, vertices, colors, indices):
        h, w = self.height, self.width
        fov_rad = math.radians(70.0)
        f = 1.0 / math.tan(fov_rad / 2.0)
        
        screen_verts = []
        for v in vertices:
            dx, dy, dz = v[0], v[1], v[2]
            yaw = 0
            cos_y = math.cos(yaw)
            sin_y = math.sin(yaw)
            rx = dx * cos_y - dz * sin_y
            rz = dx * sin_y + dz * cos_y
            pitch = 0
            cos_p = math.cos(pitch)
            sin_p = math.sin(pitch)
            ry = dy * cos_p - rz * sin_p
            rz2 = dy * sin_p + rz * cos_p
            if rz2 > 0.1:
                sx = w/2 + (rx / rz2) * f * w/2
                sy = h/2 - (ry / rz2) * f * h/2
                screen_verts.append((sx, sy, rz2))
            else:
                screen_verts.append((w/2, h/2, 0.1))
        
        for i in range(0, len(indices), 3):
            v0_idx = indices[i]
            v1_idx = indices[i+1]
            v2_idx = indices[i+2]
            v0 = screen_verts[v0_idx]
            v1 = screen_verts[v1_idx]
            v2 = screen_verts[v2_idx]
            edge1x = v1[0] - v0[0]
            edge1y = v1[1] - v0[1]
            edge2x = v2[0] - v0[0]
            edge2y = v2[1] - v0[1]
            cross = edge1x * edge2y - edge1y * edge2x
            if cross < 0:
                continue
            if v0[2] < 0.1 or v1[2] < 0.1 or v2[2] < 0.1:
                continue
            x_min = max(0, min(int(v0[0]), int(v1[0]), int(v2[0])))
            x_max = min(w-1, max(int(v0[0]), int(v1[0]), int(v2[0])))
            y_min = max(0, min(int(v0[1]), int(v1[1]), int(v2[1])))
            y_max = min(h-1, max(int(v0[1]), int(v1[1]), int(v2[1])))
            c0 = colors[v0_idx]
            c1 = colors[v1_idx]
            c2 = colors[v2_idx]
            for y in range(y_min, y_max + 1):
                for x in range(x_min, x_max + 1):
                    dx0 = x - v0[0]
                    dy0 = y - v0[1]
                    dx1 = x - v1[0]
                    dy1 = y - v1[1]
                    dx2 = x - v2[0]
                    dy2 = y - v2[1]
                    area_orig = cross
                    alpha = (dx1 * dy2 - dx2 * dy1) / area_orig
                    beta = (dx2 * dy0 - dx0 * dy2) / area_orig
                    gamma = 1.0 - alpha - beta
                    if alpha > 0 and beta > 0 and gamma > 0:
                        z = alpha * v0[2] + beta * v1[2] + gamma * v2[2]
                        if z < self.depth_buffer[y, x]:
                            self.depth_buffer[y, x] = z
                            r = alpha * c0[0] + beta * c1[0] + gamma * c2[0]
                            g = alpha * c0[1] + beta * c1[1] + gamma * c2[1]
                            b = alpha * c0[2] + beta * c1[2] + gamma * c2[2]
                            fog_factor = min(1.0, max(0.0, (z - self.fog_near) / (self.fog_far - self.fog_near)))
                            fog_color = (85, 155, 186)
                            r = int((r * 255 * (1 - fog_factor * 0.3) + fog_color[0] * fog_factor * 0.3))
                            g = int((g * 255 * (1 - fog_factor * 0.3) + fog_color[1] * fog_factor * 0.3))
                            b = int((b * 255 * (1 - fog_factor * 0.3) + fog_color[2] * fog_factor * 0.3))
                            r = max(0, min(255, r))
                            g = max(0, min(255, g))
                            b = max(0, min(255, b))
                            self.screen.set_at((x, y), (r, g, b))
                            
    def draw_block_outline(self, x, y, z, color=(255, 255, 255)):
        pass
        
    def update(self):
        pygame.display.flip()
        
    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
