# ============================================================================
# DATOTEKA: game_loop.py
# Uloga: Glavni game loop - upravlja tokom igre
# ============================================================================

import pygame
import sys
from config.constants import *
from game.map import GameMap
from game.turn_manager import TurnManager
from entities.player import Player
from entities.enemy1 import RangeEnemy, MeleeEnemy
from ui.renderer import Renderer
from prolog_comm import PrologAgent

class GameLoop:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Into The Breach - Prolog AI")
        self.clock = pygame.time.Clock()
        
        # Inicijalizacija komponenti
        self.game_map = GameMap(GRID_SIZE, GRID_SIZE)
        self.turn_manager = TurnManager()
        self.renderer = Renderer(self.screen, self.game_map)
        self.prolog_agent = PrologAgent()
        
        # Inicijalizacija entiteta
        self._init_entities()
        
        # Game state
        self.running = True
        self.paused = False
        self.game_over = False
        self.winner = None
        self.turn_delay_timer = 0
        self.waiting_for_next_turn = False
        
    def _init_entities(self):
        """Inicijalizira playera i neprijatelje na random pozicijama"""
        # Player na random poziciji
        player_pos = self.game_map.get_random_walkable_position()
        self.player = Player(player_pos[0], player_pos[1])
        
        # Neprijatelji na random pozicijama (različitim od playera)
        self.enemies = []
        
        # Range enemy
        range_pos = self.game_map.get_random_walkable_position(exclude=[player_pos])
        self.enemies.append(RangeEnemy(range_pos[0], range_pos[1]))
        
        # Melee enemy
        melee_pos = self.game_map.get_random_walkable_position(
            exclude=[player_pos, range_pos]
        )
        self.enemies.append(MeleeEnemy(melee_pos[0], melee_pos[1]))
        
    def run(self):
        """Glavni game loop"""
        self._render()  # Prikaži početno stanje
        pygame.display.flip()
        pygame.time.wait(1000)  # Pauza 1000ms (1 sekunde)
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0  # Delta time u sekundama
            
            self._handle_events()
            
            if not self.paused and not self.game_over:
                self._update(dt)
            
            self._render()
        
    def _handle_events(self):
        """Obrađuje input events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Pauza samo između turn-ova
                    if self.waiting_for_next_turn:
                        self.paused = not self.paused
                elif event.key == pygame.K_r and self.game_over:
                    # Restart igre
                    self.__init__()
    
    def _update(self, dt):
        """Update game state"""
        if self.game_over:
            return
        
        # Delay između turn-ova
        if self.waiting_for_next_turn:
            self.turn_delay_timer += dt
            if self.turn_delay_timer >= TURN_DELAY:
                self.turn_delay_timer = 0
                self.waiting_for_next_turn = False
                self.turn_manager.next_turn()
            return
        
        # Provjeri pobjedu/poraz
        if not self._check_game_state():
            return
        
        # Izvršava turn za trenutni entitet
        current_entity = self.turn_manager.get_current_entity()
        
        if current_entity == "player":
            self._execute_player_turn()
        elif current_entity == "enemies":
            self._execute_enemy_turn()
    
    
    def _execute_player_turn(self):
        """Izvršava player turn koristeći Prolog AI"""
        if self.turn_manager.actions_left <= 0:
            self.waiting_for_next_turn = True
            return
        
        # Pripremi game state za Prolog
        game_state = self._prepare_game_state()
        
        print(f"\n=== PLAYER TURN (Action {3 - self.turn_manager.actions_left}/2) ===")
        
        # Dobij akciju od Prolog agenta
        action = self.prolog_agent.get_action(game_state)
        
        if action:
            self._execute_action(self.player, action)
            self.turn_manager.use_action()
        else:
            # Nema više validnih akcija
            print("No valid actions available")
            self.waiting_for_next_turn = True
        
    def _execute_enemy_turn(self):
        """Izvršava neprijateljske turn-ove"""
        if self.turn_manager.actions_left <= 0:
            # Reset acted flags before ending turn
            for enemy in self.enemies:
                enemy.acted_this_turn = False
            self.waiting_for_next_turn = True
            return
        
        # Pronađi prvog živog neprijatelja koji još nije odigrao
        for enemy in self.enemies:
            if enemy.hp > 0 and not enemy.acted_this_turn:
                print(f"\n=== {type(enemy).__name__.upper()} TURN ===")
                
                # Debug: prikaži distance do playera
                dist = enemy.distance_to(self.player)
                print(f"  Distance to player: {dist} (grid distance)")
                print(f"  Positions: Enemy({enemy.x},{enemy.y}), Player({self.player.x},{self.player.y})")
                
                action = enemy.decide_action(
                    self.player, self.game_map, self.enemies
                )
                if action:
                    print(f"  Enemy decision: {action['type']}")
                    self._execute_action(enemy, action)
                else:
                    print("  No valid action")
                
                enemy.acted_this_turn = True
                self.turn_manager.use_action()
                return
        
        # Svi neprijatelji su odigrali - reset i wait
        for enemy in self.enemies:
            enemy.acted_this_turn = False
        self.waiting_for_next_turn = True

    def _execute_action(self, entity, action):
        "Izvršava akciju za dani entitet - radi s objektima i dictionary-ima"
        pygame.display.flip()
        pygame.time.wait(1000)  # Pauza 1000ms (1 sekunde)
        action_type = action.get('type')
        
        if action_type == 'move':
            target_pos = action.get('target')
            if self._is_valid_move(entity, target_pos):
                entity.x, entity.y = target_pos
                print(f"  → {type(entity).__name__} moved to {target_pos}")
        
        elif action_type == 'melee_attack':
            target = action.get('target')
            
            # Convert to actual object if it's a dictionary
            if isinstance(target, dict):
                target = self._get_entity_at(target['x'], target['y'])
            
            if target and hasattr(target, 'take_damage'):
                damage = action.get('damage', 2)
                target.take_damage(damage)
                print(f"  → Melee attack on {type(target).__name__} at ({target.x}, {target.y}) for {damage} damage! HP: {target.hp}")
            else:
                print(f"  → Melee attack FAILED - no valid target")
        
        elif action_type == 'melee_push':
            target = action.get('target')
            direction = action.get('direction')
            
            # Convert to actual object if it's a dictionary
            if isinstance(target, dict):
                target = self._get_entity_at(target['x'], target['y'])
            
            if target and direction and hasattr(target, 'x'):
                new_x = target.x + direction[0]
                new_y = target.y + direction[1]
                if self._is_valid_push(target, (new_x, new_y)):
                    target.x, target.y = new_x, new_y
                    print(f"  → Pushed {type(target).__name__} to ({new_x}, {new_y})")
                    # Check if pushed into water
                    if self.game_map.get_terrain(new_x, new_y) == TERRAIN_WATER:
                        target.hp = 0  # Instant death
                        print(f"  → {type(target).__name__} drowned! ☠️")
            else:
                print(f"  → Push FAILED - no valid target or direction")
        
        elif action_type == 'range_attack':
            target = action.get('target')
            
            # Convert to actual object if it's a dictionary
            if isinstance(target, dict):
                target = self._get_entity_at(target['x'], target['y'])
            
            if target and hasattr(target, 'take_damage'):
                if self._has_line_of_sight(entity, target):
                    damage = action.get('damage', 1)
                    target.take_damage(damage)
                    print(f"  → Range attack on {type(target).__name__} at ({target.x}, {target.y}) for {damage} damage! HP: {target.hp}")
                else:
                    print(f"  → Range attack FAILED - no line of sight")
            else:
                print(f"  → Range attack FAILED - no valid target")

    def _get_entity_at(self, x, y):
        """Pronalazi bilo koji entitet (player ili enemy) na zadanoj poziciji"""
        # Check player
        if self.player.x == x and self.player.y == y and self.player.hp > 0:
            return self.player
        
        # Check enemies
        for enemy in self.enemies:
            if enemy.x == x and enemy.y == y and enemy.hp > 0:
                return enemy
        
        return None

    
    def _find_enemy_at(self, x, y):
        """Pronalazi enemy objekt na zadanoj poziciji"""
        for enemy in self.enemies:
            if enemy.hp > 0 and enemy.x == x and enemy.y == y:
                return enemy
        return None
    
    def _is_valid_move(self, entity, target_pos):
        """Provjerava da li je pomak validan"""
        x, y = target_pos
        
        # Provjeri granice
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False
        
        # Provjeri terrain
        terrain = self.game_map.get_terrain(x, y)
        if terrain in [TERRAIN_MOUNTAIN, TERRAIN_WATER]:
            return False
        
        # Provjeri da li je pozicija zauzeta
        if self.player.x == x and self.player.y == y:
            return False
        for enemy in self.enemies:
            if enemy.hp > 0 and enemy.x == x and enemy.y == y:
                return False
        
        return True
    
    def _is_valid_push(self, target, new_pos):
        """Provjerava da li je push validan"""
        x, y = new_pos
        
        # Provjeri granice
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False
        
        # Push u vodu je validan (ubija)
        terrain = self.game_map.get_terrain(x, y)
        if terrain == TERRAIN_WATER:
            return True
        
        # Push u planinu nije validan
        if terrain == TERRAIN_MOUNTAIN:
            return False
        
        # Provjeri da li je pozicija zauzeta
        if self.player.x == x and self.player.y == y:
            return False
        for enemy in self.enemies:
            if enemy.hp > 0 and enemy.x == x and enemy.y == y:
                return False
        
        return True
    
    def _has_line_of_sight(self, source, target):
        """Provjerava liniju pogleda za range attack - samo planine blokiraju"""
        from config.constants import TERRAIN_MOUNTAIN
        
        # Bresenham line algorithm
        x0, y0 = source.x, source.y
        x1, y1 = target.x, target.y
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            # Skip start i end pozicije - samo provjeri tile-ove između
            if (x, y) != (x0, y0) and (x, y) != (x1, y1):
                terrain = self.game_map.get_terrain(x, y)
                if terrain == TERRAIN_MOUNTAIN:
                    return False
            
            if x == x1 and y == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        return True
    
    def _prepare_game_state(self):
        """Priprema game state za Prolog agenta"""
        # Živi neprijatelji
        alive_enemies = [
            {
                'type': type(e).__name__.lower().replace('enemy', ''),
                'x': e.x,
                'y': e.y,
                'hp': e.hp
            }
            for e in self.enemies if e.hp > 0
        ]
        
        return {
            'player': {
                'x': self.player.x,
                'y': self.player.y,
                'hp': self.player.hp
            },
            'enemies': alive_enemies,
            'terrain': self.game_map.grid,
            'actions_left': self.turn_manager.actions_left,
            'grid_size': GRID_SIZE
        }
    
    def _check_game_state(self):
        """Provjerava win/lose stanje"""
        # Provjeri da li je player mrtav
        if self.player.hp <= 0:
            self.game_over = True
            self.winner = "enemies"
            return False
        
        # Provjeri da li su svi neprijatelji mrtvi
        alive_enemies = [e for e in self.enemies if e.hp > 0]
        if not alive_enemies:
            self.game_over = True
            self.winner = "player"
            return False
        
        return True
    
    def _render(self):
        """Renderuje sve na ekran"""
        self.screen.fill(COLOR_BG)
        
        # Renderuj mapu
        self.renderer.render_map()
        
        # Renderuj entitete
        self.renderer.render_entity(self.player, COLOR_PLAYER)
        for enemy in self.enemies:
            if enemy.hp > 0:
                color = COLOR_ENEMY_RANGE if isinstance(enemy, RangeEnemy) else COLOR_ENEMY_MELEE
                self.renderer.render_entity(enemy, color)
        
        # Renderuj UI
        self.renderer.render_ui(
            self.player,
            self.enemies,
            self.turn_manager,
            self.paused,
            self.game_over,
            self.winner
        )
        
        pygame.display.flip()