# ============================================================================
# DATOTEKA: ui/renderer.py
# Uloga: Renderiranje s PyGame
# ============================================================================

import pygame
from config.constants import *

class Renderer:

    def __init__(self, screen, game_map):
        self.screen = screen
        self.game_map = game_map
        self.font = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 48)
    
    def render_map(self):
        """Renderuje grid i terrain"""
        for y in range(self.game_map.height):
            for x in range(self.game_map.width):
                terrain = self.game_map.get_terrain(x, y)
                
                # Boja prema terrain tipu
                if terrain == TERRAIN_GRASS:
                    color = COLOR_GRASS
                elif terrain == TERRAIN_MOUNTAIN:
                    color = COLOR_MOUNTAIN
                else:  # WATER
                    color = COLOR_WATER
                
                # Renderuj tile
                rect = pygame.Rect(
                    GRID_OFFSET_X + x * TILE_SIZE,
                    GRID_OFFSET_Y + y * TILE_SIZE,
                    TILE_SIZE,
                    TILE_SIZE
                )
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)
    
    def render_entity(self, entity, color):
        """Renderuje entitet (player ili enemy)"""
        center_x = GRID_OFFSET_X + entity.x * TILE_SIZE + TILE_SIZE // 2
        center_y = GRID_OFFSET_Y + entity.y * TILE_SIZE + TILE_SIZE // 2
        
        pygame.draw.circle(
            self.screen,
            color,
            (center_x, center_y),
            TILE_SIZE // 3
        )
        
        # HP bar
        self._render_hp_bar(entity, center_x, center_y - TILE_SIZE // 2)
    
    def _render_hp_bar(self, entity, x, y):
        """Renderuje HP bar iznad entiteta"""
        bar_width = TILE_SIZE - 10
        bar_height = 5
        
        # Background
        bg_rect = pygame.Rect(x - bar_width // 2, y, bar_width, bar_height)
        pygame.draw.rect(self.screen, (100, 100, 100), bg_rect)
        
        # HP
        hp_ratio = entity.hp / entity.max_hp
        hp_width = int(bar_width * hp_ratio)
        hp_rect = pygame.Rect(x - bar_width // 2, y, hp_width, bar_height)
        pygame.draw.rect(self.screen, (0, 255, 0), hp_rect)
    
    def render_ui(self, player, enemies, turn_manager, paused, game_over, winner):
        """Renderuje UI informacije"""
        ui_x = GRID_OFFSET_X + GRID_SIZE * TILE_SIZE + 40
        ui_y = 50
        
        # Turn info
        turn_text = f"Turn: {turn_manager.turn_number}"
        current_text = f"Current: {turn_manager.current_turn.capitalize()}"
        actions_text = f"Actions left: {turn_manager.actions_left}"
        
        self._render_text(turn_text, ui_x, ui_y)
        self._render_text(current_text, ui_x, ui_y + 30)
        self._render_text(actions_text, ui_x, ui_y + 60)
        
        # Player info
        self._render_text("=== PLAYER ===", ui_x, ui_y + 110)
        self._render_text(f"HP: {player.hp}/{player.max_hp}", ui_x, ui_y + 140)
        self._render_text(f"Pos: ({player.x}, {player.y})", ui_x, ui_y + 170)
        
        # Enemies info
        self._render_text("=== ENEMIES ===", ui_x, ui_y + 220)
        y_offset = 250
        alive_enemies = [e for e in enemies if e.hp > 0]
        for i, enemy in enumerate(alive_enemies):
            enemy_type = type(enemy).__name__
            text = f"{enemy_type}: HP {enemy.hp}"
            self._render_text(text, ui_x, ui_y + y_offset + i * 30)
        
        # Instructions
        self._render_text("SPACE - Pause", ui_x, SCREEN_HEIGHT - 100, size=20)
        
        # Pause overlay
        if paused:
            self._render_overlay("PAUSED", COLOR_PAUSE)
        
        # Game over overlay
        if game_over:
            if winner == "player":
                self._render_overlay("PLAYER WINS!", COLOR_WIN)
            else:
                self._render_overlay("ENEMIES WIN!", COLOR_LOSE)
            
            restart_text = "Press R to restart"
            self._render_text(restart_text, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, size=24)
    
    def _render_text(self, text, x, y, size=24):
        """Renderuje tekst"""
        if size == 24:
            font = self.font
        elif size == 48:
            font = self.font_large
        else:
            font = pygame.font.Font(None, size)
        
        surface = font.render(text, True, COLOR_TEXT)
        self.screen.blit(surface, (x, y))
    
    def _render_overlay(self, text, color):
        """Renderuje overlay za pause/game over"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Text
        text_surface = self.font_large.render(text, True, color)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(text_surface, text_rect)