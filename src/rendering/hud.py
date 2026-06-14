"""Heads-up display for the game."""

import pygame
import sys
from src.core.config import WINDOW_WIDTH, WINDOW_HEIGHT
from src.world.blocks import HOTBAR_BLOCKS, BLOCK_DATA


class HUD:
    """In-game heads-up display."""
    
    def __init__(self):
        self.font_large = pygame.font.SysFont('consolas,monospace', 36, bold=True)
        self.font_medium = pygame.font.SysFont('consolas,monospace', 24)
        self.font_small = pygame.font.SysFont('consolas,monospace', 18)
        self.hotbar_slots = 9
        self.slot_size = 48
        self.crosshair_size = 20
    
    def draw(self, screen, player, world, fps: int = 0, chunks_loaded: int = 0):
        """Draw the complete HUD."""
        # Crosshair
        cx, cy = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2
        cross_color = (255, 255, 255)
        pygame.draw.line(screen, cross_color, (cx - 10, cy), (cx - 4, cy), 2)
        pygame.draw.line(screen, cross_color, (cx + 4, cy), (cx + 10, cy), 2)
        pygame.draw.line(screen, cross_color, (cx, cy - 10), (cx, cy - 4), 2)
        pygame.draw.line(screen, cross_color, (cx, cy + 4), (cx, cy + 10), 2)
        
        # Hotbar
        self._draw_hotbar(screen, player)
        
        # FPS and debug info
        self._draw_debug_info(screen, fps, chunks_loaded, player)
        
        # Controls help
        self._draw_controls(screen)
    
    def _draw_hotbar(self, screen, player):
        """Draw the hotbar with block slots."""
        hotbar_y = WINDOW_HEIGHT - self.slot_size - 20
        hotbar_width = self.hotbar_slots * (self.slot_size + 4)
        hotbar_x = (WINDOW_WIDTH - hotbar_width) // 2
        
        # Hotbar background
        pygame.draw.rect(screen, (60, 60, 60), 
                        (hotbar_x - 4, hotbar_y - 4, 
                         hotbar_width + 8, self.slot_size + 8))
        pygame.draw.rect(screen, (100, 100, 100),
                        (hotbar_x - 4, hotbar_y - 4,
                         hotbar_width + 8, self.slot_size + 8), 2)
        
        # Draw slots
        for i in range(self.hotbar_slots):
            slot_x = hotbar_x + i * (self.slot_size + 4)
            is_selected = (i == player.selected_slot)
            
            # Slot background
            color = (80, 80, 80) if is_selected else (60, 60, 60)
            pygame.draw.rect(screen, color, 
                           (slot_x, hotbar_y, self.slot_size, self.slot_size))
            
            if is_selected:
                pygame.draw.rect(screen, (255, 255, 255),
                               (slot_x, hotbar_y, self.slot_size, self.slot_size), 2)
            
            # Block icon
            if i < len(HOTBAR_BLOCKS):
                block_type = HOTBAR_BLOCKS[i]
                block_name = BLOCK_DATA.get(block_type, {}).get("name", "Unknown")
                color = self._get_block_color(block_type)
                
                # Draw block icon (small cube representation)
                icon_x = slot_x + self.slot_size // 2
                icon_y = hotbar_y + self.slot_size // 2
                icon_size = 12
                
                # Top face
                pygame.draw.polygon(screen, (color[0]+30, color[1]+30, color[2]+30),
                                  [(icon_x, icon_y - icon_size),
                                   (icon_x + icon_size, icon_y - icon_size//2),
                                   (icon_x, icon_y),
                                   (icon_x - icon_size, icon_y - icon_size//2)])
                # Left face
                pygame.draw.polygon(screen, (color[0], color[1], color[2]),
                                  [(icon_x - icon_size, icon_y - icon_size//2),
                                   (icon_x, icon_y),
                                   (icon_x, icon_y + icon_size),
                                   (icon_x - icon_size, icon_y + icon_size//2)])
                # Right face
                pygame.draw.polygon(screen, (color[0]-30, color[1]-30, color[2]-30),
                                  [(icon_x + icon_size, icon_y - icon_size//2),
                                   (icon_x, icon_y),
                                   (icon_x, icon_y + icon_size),
                                   (icon_x + icon_size, icon_y + icon_size//2)])
    
    def _get_block_color(self, block_type) -> tuple:
        """Get color for a block type icon."""
        colors = {
            1: (85, 170, 60),    # Grass
            2: (120, 90, 50),    # Dirt
            3: (128, 128, 128),  # Stone
            4: (90, 65, 40),     # Wood
            5: (40, 120, 30),    # Leaves
            6: (210, 200, 140),  # Sand
            8: (100, 100, 100),  # Cobblestone
            9: (170, 135, 75),   # Planks
            17: (160, 80, 70),   # Brick
            14: (50, 50, 50),    # Bedrock
        }
        return colors.get(int(block_type), (128, 128, 128))
    
    def _draw_debug_info(self, screen, fps: int, chunks_loaded: int, player):
        """Draw debug information."""
        # FPS
        fps_text = self.font_small.render(f"FPS: {fps}", True, (255, 255, 255))
        screen.blit(fps_text, (10, 10))
        
        # Chunks loaded
        chunks_text = self.font_small.render(f"Chunks: {chunks_loaded}", True, (255, 255, 255))
        screen.blit(chunks_text, (10, 30))
        
        # Position
        pos = player.get_position()
        pos_text = self.font_small.render(
            f"Pos: {pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f}",
            True, (255, 255, 255))
        screen.blit(pos_text, (10, 50))
    
    def _draw_controls(self, screen):
        """Draw control hints."""
        controls_text = self.font_small.render(
            "WASD: Move | Space: Jump | Shift: Sprint | LMB: Break | RMB: Place | 1-9: Select Block",
            True, (200, 200, 200))
        screen.blit(controls_text, (10, WINDOW_HEIGHT - 60))
        
        escape_text = self.font_small.render("ESC: Pause | F3: Debug", True, (200, 200, 200))
        screen.blit(escape_text, (10, WINDOW_HEIGHT - 40))
    
    def draw_pause_menu(self, screen):
        """Draw the pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font_large.render("PAUSED", True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//3))
        screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "Click to resume",
            "Press ESC to quit"
        ]
        
        for i, text in enumerate(instructions):
            surface = self.font_medium.render(text, True, (200, 200, 200))
            rect = surface.get_rect(center=(WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + i * 40))
            screen.blit(surface, rect)
