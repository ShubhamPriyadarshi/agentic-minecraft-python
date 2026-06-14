"""Main game class managing the game loop and state."""

import pygame
import OpenGL.GL as gl
import numpy as np
import platform
from src.core.config import (WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
                             TARGET_FPS, LOAD_DISTANCE, DAY_CYCLE_DURATION,
                             FOG_NEAR, FOG_FAR)
from src.world.world import World
from src.world.blocks import HOTBAR_BLOCKS, BlockType, generate_block_textures
from src.world.chunk import Chunk
from src.rendering.renderer import Renderer, IS_MACOS_ARM
from src.rendering.hud import HUD
from src.game.player import Player
from src.game.particles import ParticleSystem


class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        
        self.running = True
        self.paused = False
        self.first_run = True
        
        # Initialize components
        self.renderer = Renderer(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.hud = HUD()
        
        # Create world
        self.world = World(seed=42, create_new=True)
        
        # Create player
        self.player = Player(self.world, x=0, y=70, z=0)
        
        # Generate initial textures
        self.textures = generate_block_textures()
        
        # Generate initial chunks
        self._generate_initial_chunks()
        
        # Game state
        self.clock = pygame.time.Clock()
        self.fps = 0
        self.chunk_load_timer = 0
        
        # Block highlight
        self.highlight_pos = None
        
        # Particle system
        self.particles = ParticleSystem()
        
        # Capture mouse on first click
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
    
    def _generate_initial_chunks(self):
        """Generate and mesh all initial chunks."""
        # Generate chunks around player
        self.world.load_chunks_around(0, 0)
        
        # Build meshes
        self.world.rebuild_all_meshes(self.textures)
    
    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0
            self.fps = self.clock.get_fps()
            
            self._handle_events()
            
            if not self.paused:
                self._update(dt)
            
            self._render()
        
        self._cleanup()
    
    def _handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    if not self.paused:
                        pygame.mouse.set_visible(False)
                        pygame.event.set_grab(True)
                    else:
                        pygame.mouse.set_visible(True)
                        pygame.event.set_grab(False)
                elif event.key == pygame.K_r:
                    # Regenerate world
                    self.world = World(seed=np.random.randint(0, 2**31), create_new=True)
                    self.player = Player(self.world, x=0, y=70, z=0)
                    self._generate_initial_chunks()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:  # Scroll up
                    self.player.selected_slot = (self.player.selected_slot - 1) % len(HOTBAR_BLOCKS)
                elif event.button == 5:  # Scroll down
                    self.player.selected_slot = (self.player.selected_slot + 1) % len(HOTBAR_BLOCKS)
                elif event.button == 1:  # Left click - break block
                    if not self.paused:
                        self._break_block()
                elif event.button == 3:  # Right click - place block
                    if not self.paused:
                        self._place_block()
            
            elif event.type == pygame.KEYDOWN:
                # Number keys for hotbar selection
                if event.key >= pygame.K_1 and event.key <= pygame.K_9:
                    idx = event.key - pygame.K_1
                    if idx < len(HOTBAR_BLOCKS):
                        self.player.selected_slot = idx
            
            elif event.type == pygame.MOUSEMOTION:
                if not self.paused:
                    dx, dy = event.rel
                    self.player.handle_mouse(dx, dy)
            
            elif event.type == pygame.VIDEORESIZE:
                self.renderer.resize(event.w, event.h)
    
    def _update(self, dt: float):
        """Update game state."""
        # Get key state
        keys = pygame.key.get_pressed()
        self.player.handle_keys(keys)
        
        # Update player
        self.player.update(dt)
        
        # Update particles
        self.particles.update(dt)
        
        # Load/unload chunks periodically
        self.chunk_load_timer += dt
        if self.chunk_load_timer > 0.5:
            pos = self.player.get_position()
            self.world.load_chunks_around(int(pos[0]), int(pos[2]))
            self.world.rebuild_dirty_meshes(self.textures)
            self.chunk_load_timer = 0
    
    def _render(self):
        """Render the game."""
        self.renderer.clear()
        
        # Get player state
        pos = self.player.get_position()
        rot = self.player.get_rotation()
        
        # Setup camera
        look_x = -np.sin(np.radians(rot[1])) * np.cos(np.radians(rot[0]))
        look_y = np.sin(np.radians(rot[0]))
        look_z = -np.cos(np.radians(rot[1])) * np.cos(np.radians(rot[0]))
        
        target = np.array([pos[0] + look_x, pos[1] + look_y, pos[2] + look_z])
        
        view = self.renderer.setup_camera(pos, target)
        
        # Setup projection
        proj = self.renderer.setup_projection(fov=70.0)
        
        # Update shader uniforms
        gl.glUseProgram(self.renderer.chunk_shader)
        
        proj_loc = gl.glGetUniformLocation(self.renderer.chunk_shader, "projection")
        view_loc = gl.glGetUniformLocation(self.renderer.chunk_shader, "view")
        
        gl.glUniformMatrix4fv(view_loc, 1, False, view.astype(np.float32).flatten())
        gl.glUniformMatrix4fv(proj_loc, 1, False, proj.astype(np.float32).flatten())
        
        # Draw skybox (OpenGL only)
        if not IS_MACOS_ARM:
            gl.glUseProgram(self.renderer.sky_shader)
            sky_proj_loc = gl.glGetUniformLocation(self.renderer.sky_shader, "projection")
            sky_view_loc = gl.glGetUniformLocation(self.renderer.sky_shader, "view")
            proj_matrix = gl.glGetFloatv(gl.GL_PROJECTION_MATRIX)
            view_matrix = gl.glGetFloatv(gl.GL_MODELVIEW_MATRIX)
            gl.glUniformMatrix4fv(sky_proj_loc, 1, False, proj_matrix.astype(np.float32).flatten())
            gl.glUniformMatrix4fv(sky_view_loc, 1, False, view_matrix.astype(np.float32).flatten())
            self.renderer.draw_skybox()
            gl.glUseProgram(self.renderer.chunk_shader)
        
        # Draw chunks
        if IS_MACOS_ARM:
            # Software renderer
            chunks = list(self.world.chunks.values())
            for chunk in chunks:
                if chunk.has_mesh and chunk.vertices.size > 0:
                    num_verts = len(chunk.vertices)
                    indices = []
                    for i in range(0, num_verts, 4):
                        indices.extend([i, i+1, i+2, i, i+2, i+3])
                    self.renderer.render_chunk(chunk.vertices, chunk.colors, indices)
        else:
            # OpenGL renderer
            gl.glEnable(gl.GL_DEPTH_TEST)
            gl.glDisable(gl.GL_BLEND)
            
            chunks = list(self.world.chunks.values())
            for chunk in chunks:
                if chunk.has_mesh and chunk.vertices.size > 0:
                    if not chunk.vao or chunk.mesh_dirty:
                        if chunk.vbo:
                            gl.glDeleteBuffers(1, [chunk.vbo])
                        if chunk.ibo:
                            gl.glDeleteBuffers(1, [chunk.ibo])
                        if chunk.vao:
                            gl.glDeleteVertexArrays(1, [chunk.vao])
                        
                        if chunk.vertices.size > 0:
                            chunk.vbo = gl.glGenBuffers(1)
                            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, chunk.vbo)
                            gl.glBufferData(gl.GL_ARRAY_BUFFER, chunk.vertices, gl.GL_STATIC_DRAW)
                            
                            color_vbo = gl.glGenBuffers(1)
                            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, color_vbo)
                            gl.glBufferData(gl.GL_ARRAY_BUFFER, chunk.colors, gl.GL_STATIC_DRAW)
                            
                            num_verts = len(chunk.vertices)
                            indices = []
                            for i in range(0, num_verts, 4):
                                indices.extend([i, i+1, i+2, i, i+2, i+3])
                            indices_arr = np.array(indices, dtype=np.uint32)
                            
                            chunk.ibo = gl.glGenBuffers(1)
                            gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, chunk.ibo)
                            gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices_arr, gl.GL_STATIC_DRAW)
                            chunk.index_count = len(indices)
                            
                            chunk.vao = gl.glGenVertexArrays(1)
                            gl.glBindVertexArray(chunk.vao)
                            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, chunk.vbo)
                            gl.glEnableVertexAttribArray(0)
                            gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 12, None)
                            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, color_vbo)
                            gl.glEnableVertexAttribArray(1)
                            gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False, 12, None)
                            gl.glBindVertexArray(0)
                            gl.glDeleteBuffers(1, [color_vbo])
                    
                    self.renderer.draw_chunk(chunk.vao, chunk.vbo, chunk.ibo, chunk.index_count)
        
        # Draw block highlight
        if self.highlight_pos:
            hx, hy, hz = self.highlight_pos
            self.renderer.draw_block_highlight(
                hx, hy, hz,
                hx + 1, hy + 1, hz + 1
            )
        
        # Draw particles
        gl.glUseProgram(0)  # Use default pipeline for particles
        self.particles.render()
        
        # Draw HUD
        self.hud.draw(pygame.display.get_surface(), self.player, self.world,
                     self.fps, len(self.world.chunks))
        
        if self.paused:
            self.hud.draw_pause_menu(pygame.display.get_surface())
        
        self.renderer.swap_buffers()
    
    def _break_block(self):
        """Break the block the player is looking at."""
        result = self.player.raycast()
        if result:
            _, _, _, bx, by, bz = result
            block = self.world.get_block(bx, by, bz)
            if block != BlockType.AIR.value:
                self.particles.spawn_break_particles(bx, by, bz, block)
            self.player.break_block(bx, by, bz)
    
    def _place_block(self):
        """Place a block at the targeted position."""
        result = self.player.raycast()
        if result:
            px, py, pz, _, _, _ = result
            block_type = HOTBAR_BLOCKS[self.player.selected_slot]
            self.player.place_block(px, py, pz, block_type)
    
    def _cleanup(self):
        """Clean up resources."""
        self.renderer.cleanup()
        pygame.quit()
