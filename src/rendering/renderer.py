"""Main OpenGL renderer for the Minecraft game."""

import OpenGL.GL as gl
import numpy as np
import pygame
from pygame.locals import DOUBLEBUF, OPENGL, RESIZABLE
from src.core.config import WINDOW_WIDTH, WINDOW_HEIGHT, FOG_NEAR, FOG_FAR
from src.rendering.opengl_utils import create_shader_program
from src.rendering.shaders import (VERTEX_SHADER_PROPER, FRAGMENT_SHADER_PROPER,
                                   VERTEX_SHADER_SKY, FRAGMENT_SHADER_SKY,
                                   VERTEX_SHADER_LINES, FRAGMENT_SHADER_LINES)


class Renderer:
    """OpenGL renderer managing display and rendering state."""
    
    def __init__(self, width: int = WINDOW_WIDTH, height: int = WINDOW_HEIGHT):
        self.width = width
        self.height = height
        
        # Initialize Pygame OpenGL context
        pygame.init()
        try:
            pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | RESIZABLE)
        except pygame.error:
            # Fallback to non-OpenGL mode for headless environments
            pygame.display.set_mode((width, height), DOUBLEBUF)
            return
        pygame.display.set_caption("Minecraft Python Edition")
        
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        gl.glCullFace(gl.GL_BACK)
        gl.glFrontFace(gl.GL_CCW)
        
        # Enable blending for transparent blocks
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        
        # Setup shaders
        self.chunk_shader = create_shader_program(VERTEX_SHADER_PROPER, FRAGMENT_SHADER_PROPER)
        self.sky_shader = create_shader_program(VERTEX_SHADER_SKY, FRAGMENT_SHADER_SKY)
        self.line_shader = create_shader_program(VERTEX_SHADER_LINES, FRAGMENT_SHADER_LINES)
        
        # Setup projection
        self._update_projection(width, height)
        
        # Setup skybox
        self._setup_skybox()
        
        # Setup VAO for lines (block highlights)
        self.highlight_vao = 0
        self.highlight_vbo = 0
        self.highlight_count = 0
        
    def _update_projection(self, width: int, height: int):
        """Update the projection matrix."""
        self.width = width
        self.height = height
        gl.glViewport(0, 0, width, height)
    
    def resize(self, width: int, height: int):
        """Handle window resize."""
        self._update_projection(width, height)
    
    def _setup_skybox(self):
        """Setup skybox geometry (a large cube)."""
        # Skybox is a large cube centered at origin
        s = 500.0
        sky_vertices = np.array([
            # x, y, z
            -s, -s,  s,   s, -s,  s,   s,  s,  s,  -s,  s,  s,  # Front
             s, -s, -s,  -s, -s, -s,  -s,  s, -s,   s,  s, -s,  # Back
            -s, -s, -s,  -s, -s,  s,   s, -s,  s,   s, -s, -s,  # Bottom
             s,  s, -s,   s,  s,  s,  -s,  s,  s,  -s,  s, -s,  # Top
            -s, -s, -s,  -s,  s, -s,  -s,  s,  s,  -s, -s,  s,  # Left
             s, -s,  s,   s,  s,  s,   s,  s, -s,   s, -s, -s,  # Right
        ], dtype=np.float32)
        
        sky_indices = np.array([
            0, 1, 2,  0, 2, 3,     # Front
            4, 5, 6,  4, 6, 7,     # Back
            8, 9, 10, 8, 10, 11,   # Bottom
            12, 13, 14, 12, 14, 15, # Top
            16, 17, 18, 16, 18, 19, # Left
            20, 21, 22, 20, 22, 23, # Right
        ], dtype=np.uint32)
        
        self.sky_vao = gl.glGenVertexArrays(1)
        self.sky_vbo = gl.glGenBuffers(1)
        self.sky_ibo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(self.sky_vao)
        
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.sky_vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, sky_vertices, gl.GL_STATIC_DRAW)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
        gl.glEnableVertexAttribArray(0)
        
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, self.sky_ibo)
        gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, sky_indices, gl.GL_STATIC_DRAW)
        
        gl.glBindVertexArray(0)
        self.sky_index_count = len(sky_indices)
    
    def set_chunk_mesh(self, chunk_vao: int, chunk_vbo: int, chunk_ibo: int, count: int):
        """Set the mesh data for rendering."""
        self.current_vao = chunk_vao
        self.current_vbo = chunk_vbo
        self.current_ibo = chunk_ibo
        self.current_index_count = count
    
    def draw_chunk(self, vao: int, vbo: int, ibo: int, index_count: int):
        """Draw a single chunk."""
        gl.glBindVertexArray(vao)
        gl.glDrawElements(gl.GL_TRIANGLES, index_count, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)
    
    def draw_skybox(self):
        """Draw the skybox."""
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        gl.glUseProgram(self.sky_shader)
        
        # Get uniform locations
        proj_loc = gl.glGetUniformLocation(self.sky_shader, "projection")
        view_loc = gl.glGetUniformLocation(self.sky_shader, "view")
        sky_top_loc = gl.glGetUniformLocation(self.sky_shader, "sky_top")
        sky_bottom_loc = gl.glGetUniformLocation(self.sky_shader, "sky_bottom")
        
        # Get current matrices from OpenGL state
        proj_matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        view_matrix = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        
        gl.glUniformMatrix4fv(proj_loc, 1, False, proj_matrix.astype(np.float32).flatten())
        gl.glUniformMatrix4fv(view_loc, 1, False, view_matrix.astype(np.float32).flatten())
        
        # Sky colors (daytime)
        gl.glUniform3f(sky_top_loc, 0.2, 0.4, 0.8)
        gl.glUniform3f(sky_bottom_loc, 0.53, 0.61, 0.73)
        
        gl.glBindVertexArray(self.sky_vao)
        gl.glDrawElements(gl.GL_TRIANGLES, self.sky_index_count, gl.GL_UNSIGNED_INT, None)
        gl.glBindVertexArray(0)
        
        gl.glEnable(gl.GL_DEPTH_TEST)
    
    def draw_block_highlight(self, x1: float, y1: float, z1: float, 
                              x2: float, y2: float, z2: float):
        """Draw a wireframe box around a block."""
        vertices = np.array([
            # Box corners
            x1, y1, z1,  x2, y1, z1,
            x2, y1, z1,  x2, y1, z2,
            x2, y1, z2,  x1, y1, z2,
            x1, y1, z2,  x1, y1, z1,
            x1, y2, z1,  x2, y2, z1,
            x2, y2, z1,  x2, y2, z2,
            x2, y2, z2,  x1, y2, z2,
            x1, y2, z2,  x1, y2, z1,
            x1, y1, z1,  x1, y2, z1,
            x2, y1, z1,  x2, y2, z1,
            x2, y1, z2,  x2, y2, z2,
            x1, y1, z2,  x1, y2, z2,
        ], dtype=np.float32)
        
        gl.glUseProgram(self.line_shader)
        
        proj_loc = gl.glGetUniformLocation(self.line_shader, "projection")
        view_loc = gl.glGetUniformLocation(self.line_shader, "view")
        color_loc = gl.glGetUniformLocation(self.line_shader, "line_color")
        
        proj_matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
        view_matrix = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
        
        gl.glUniformMatrix4fv(proj_loc, 1, False, proj_matrix.astype(np.float32).flatten())
        gl.glUniformMatrix4fv(view_loc, 1, False, view_matrix.astype(np.float32).flatten())
        gl.glUniform3f(color_loc, 0.0, 0.0, 0.0)
        
        vao = gl.glGenVertexArrays(1)
        vbo = gl.glGenBuffers(1)
        
        gl.glBindVertexArray(vao)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices, gl.GL_DYNAMIC_DRAW)
        gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
        gl.glEnableVertexAttribArray(0)
        
        gl.glDrawArrays(gl.GL_LINES, 0, 24)
        
        gl.glDeleteBuffers(1, [vbo])
        gl.glDeleteVertexArrays(1, [vao])
    
    def setup_camera(self, position, target, up=(0, 1, 0)):
        """Setup camera using lookAt matrix."""
        # Compute view matrix manually
        z = np.array(position) - np.array(target)
        z = z / np.linalg.norm(z)
        x = np.cross(np.array(up), z)
        x = x / np.linalg.norm(x)
        y = np.cross(z, x)
        
        view = np.array([
            [x[0], y[0], z[0], 0],
            [x[1], y[1], z[1], 0],
            [x[2], y[2], z[2], 0],
            [-np.dot(x, position), -np.dot(y, position), -np.dot(z, position), 1],
        ], dtype=np.float32).T
        
        return view
    
    def setup_projection(self, fov: float = 70.0, near: float = 0.1, far: float = 500.0):
        """Setup perspective projection matrix."""
        aspect = self.width / self.height
        fov_rad = np.radians(fov)
        
        f = 1.0 / np.tan(fov_rad / 2.0)
        
        projection = np.array([
            [f / aspect, 0, 0, 0],
            [0, f, 0, 0],
            [0, 0, (far + near) / (near - far), -1],
            [0, 0, (2 * far * near) / (near - far), 0],
        ], dtype=np.float32)
        
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadMatrixf(projection)
        
        return projection
    
    def clear(self):
        """Clear the screen."""
        gl.glClearColor(0.53, 0.61, 0.73, 1.0)  # Sky blue
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    
    def swap_buffers(self):
        """Swap display buffers."""
        pygame.display.flip()
    
    def cleanup(self):
        """Clean up OpenGL resources."""
        for attr in ['sky_vao', 'sky_vbo', 'sky_ibo', 'current_vao', 'current_vbo', 'current_ibo']:
            if hasattr(self, attr) and getattr(self, attr, 0):
                gl_func = getattr(gl, f'glDelete{attr.split("_")[0].upper()}s')
                gl_func(1, [getattr(self, attr)])
