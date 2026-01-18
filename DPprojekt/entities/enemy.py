import random
from game.pathfinding import get_next_move_towards, get_next_move_away_from

class Enemy:
    """Base klasa za sve neprijatelje"""
    def __init__(self, x, y, hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = hp
        self.acted_this_turn = False
    
    def take_damage(self, damage):
        """Prima damage"""
        self.hp = max(0, self.hp - damage)
    
    def is_alive(self):
        """Provjerava da li je živ"""
        return self.hp > 0
    
    def manhattan_distance(self, target):
        """Manhattan distance do targeta"""
        return abs(self.x - target.x) + abs(self.y - target.y)
    
    def chebyshev_distance(self, target):
        """Chebyshev distance do targeta (grid distance)"""
        return max(abs(self.x - target.x), abs(self.y - target.y))
    
    def distance_to(self, target):
        """Glavni distance method - koristi Chebyshev"""
        return self.chebyshev_distance(target)
    
    def decide_action(self, player, game_map, other_enemies):
        """
        Odlučuje koju akciju izvršiti
        Override u child klasama
        """
        raise NotImplementedError
    
    def _get_occupied_positions(self, player, other_enemies):
        """Vraća liste zauzenih pozicija"""
        occupied = [(player.x, player.y)]
        for enemy in other_enemies:
            if enemy.hp > 0 and enemy != self:
                occupied.append((enemy.x, enemy.y))
        return occupied


class RangeEnemy(Enemy):
    """Range neprijatelj - napada s distance, drži se dalje od playera"""
    def __init__(self, x, y):
        super().__init__(x, y, hp=3)
        self.attack_range = 2  # Grid distance 2
        self.preferred_distance = 2
    
    def decide_action(self, player, game_map, other_enemies):
        """
        Strategija: 
        - Ako je player u range-u (1-2) i IMA LOS -> napadni
        - Ako je player u range-u ali NEMA LOS -> pomakni se
        - Ako je player izvan range-a -> pomakni se
        """
        distance = self.distance_to(player)
        
        # PRIORITET 1: Ako je u attack range-u, provjeri LOS
        if distance <= self.attack_range:
            if self._has_line_of_sight(player, game_map):
                # Ima LOS - pucaj!
                return {
                    'type': 'range_attack',
                    'target': player,
                    'damage': 1
                }
            # U range-u ali NEMA LOS - idi se maknuti da dobiješ LOS
            # Fall through to movement
        
        # PRIORITET 2: Približi se ili se pomakni za bolju poziciju
        occupied = self._get_occupied_positions(player, other_enemies)
        move_pos = get_next_move_towards(self, player, game_map, occupied)
        
        if move_pos:
            return {
                'type': 'move',
                'target': move_pos
            }
        
        return None
    
    def _has_line_of_sight(self, target, game_map):
        """Provjerava da li ima liniju pogleda do targeta - samo planine blokiraju"""
        from config.constants import TERRAIN_MOUNTAIN
        
        # Bresenham line algorithm za provjeru svih tile-ova između
        x0, y0 = self.x, self.y
        x1, y1 = target.x, target.y
        
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        x, y = x0, y0
        
        while True:
            # Skip start i end pozicije
            if (x, y) != (x0, y0) and (x, y) != (x1, y1):
                if game_map.get_terrain(x, y) == TERRAIN_MOUNTAIN:
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


class MeleeEnemy(Enemy):
    """Melee neprijatelj - agresivno se približava playeru"""
    def __init__(self, x, y):
        super().__init__(x, y, hp=4)
        self.actions_per_turn = 2
    
    def decide_action(self, player, game_map, other_enemies):
        """
        Strategija:
        - Ako je player adjacent (grid distance 1 - SVI tile-ovi oko njega) -> napadni
        - Inače -> približi se playeru koristeći pathfinding
        """
        distance = self.distance_to(player)
        
        # Debug: provjeri grid distance
        # print(f"  DEBUG MeleeEnemy: distance to player = {distance}, positions: self({self.x},{self.y}), player({player.x},{player.y})")
        
        # Ako je grid distance 1 (svi tile-ovi oko njega, i dijagonale), napadni
        if distance == 1:
            return {
                'type': 'melee_attack',
                'target': player,
                'damage': 2
            }
        
        # Inače se pomakni prema playeru koristeći pathfinding
        occupied = self._get_occupied_positions(player, other_enemies)
        move_pos = get_next_move_towards(self, player, game_map, occupied)
        
        if move_pos:
            return {
                'type': 'move',
                'target': move_pos
            }
        
        return None
