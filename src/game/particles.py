"""Particle system for block breaking effects."""

import numpy as np
import pygame
import OpenGL.GL as gl
from src.world.blocks import get_block_color


class Particle:
    """A single particle."""
    
    __slots__ = ['pos', 'vel', 'color', 'life', 'max_life', 'size']
    
    def __init__(self, pos: np.ndarray, vel: np.ndarray, color: tuple, 
                 life: float = 1.0, size: float = 0.1):
        self.pos = pos.copy()
        self.vel = vel.copy()
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size


class ParticleSystem:
    """Manages particles for visual effects."""
    
    def __init__(self):
        self.particles: list = []
        self.vao = 0
        self.vbo = 0
    
    def spawn_break_particles(self, x: int, y: int, z: int, block_type: int):
        """Spawn particles when a block is broken."""
        color = get_block_color(block_type)
        
        for _ in range(8):
            pos = np.array([
                x + np.random.uniform(0.2, 0.8),
                y + np.random.uniform(0.2, 0.8),
                z + np.random.uniform(0.2, 0.8),
            ], dtype=np.float32)
            
            vel = np.array([
                np.random.uniform(-2, 2),
                np.random.uniform(1, 4),
                np.random.uniform(-2, 2),
            ], dtype=np.float32)
            
            particle = Particle(pos, vel, color, life=1.0, size=0.08)
            self.particles.append(particle)
    
    def update(self, dt: float):
        """Update all particles."""
        gravity = -9.8
        
        for p in self.particles:
            p.vel[1] += gravity * dt
            p.pos += p.vel * dt
            p.life -= dt
            
            # Bounce off ground
            if p.pos[1] < 0:
                p.pos[1] = 0
                p.vel[1] = abs(p.vel[1]) * 0.5
                p.vel[0] *= 0.8
                p.vel[2] *= 0.8
        
        # Remove dead particles
        self.particles = [p for p in self.particles if p.life > 0]
    
    def render(self):
        """Render particles as point sprites."""
        if not self.particles:
            return
        
        vertices = []
        for p in self.particles:
            alpha = p.life / p.max_life
            size = p.size * alpha
            
            x, y, z = p.pos
            r, g, b = p.color
            
            # Point sprite (quad)
            vertices.extend([
                x - size, y - size, z, r, g, b,
                x + size, y - size, z, r, g, b,
                x + size, y + size, z, r, g, b,
                x - size, y + size, z, r, g, b,
            ])
        
        if vertices:
            arr = np.array(vertices, dtype=np.float32)
            
            vbo = gl.glGenBuffers(1)
            vao = gl.glGenVertexArrays(1)
            
            gl.glEnable(gl.GL_BLEND)
            gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
            gl.glDisable(gl.GL_DEPTH_TEST)
            
            gl.glBindVertexArray(vao)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
            gl.glBufferData(gl.GL_ARRAY_BUFFER, arr, gl.GL_DYNAMIC_DRAW)
            gl.glVertexAttribPointer(0, 6, gl.GL_FLOAT, False, 24, None)
            gl.glEnableVertexAttribArray(0)
            
            gl.glDrawArrays(gl.GL_TRIANGLE_FAN, 0, len(vertices) // 6 * 4)
            
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            
            gl.glDeleteBuffers(1, [vbo])
            gl.glDeleteVertexArrays(1, [vao])
    
    def clear(self):
        """Clear all particles."""
        self.particles.clear()
