# ============================================================================
# DATOTEKA: entities/player.py
# Uloga: Player entitet
# ============================================================================

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 5
        self.max_hp = 5
        
        # Akcije
        self.actions_per_turn = 2
        
        # Attack ranges
        self.melee_range = 1
        self.range_attack_range = 2  # 2 pločice dalje od playera
    
    def take_damage(self, damage):
        """Prima damage"""
        self.hp = max(0, self.hp - damage)
    
    def is_alive(self):
        """Provjerava da li je živ"""
        return self.hp > 0
    
    def get_adjacent_positions(self):
        """Vraća susjedne pozicije (za melee)"""
        return [
            (self.x + dx, self.y + dy)
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
        ]
    
    def manhattan_distance(self, target):
        """Manhattan distance do targeta"""
        return abs(self.x - target.x) + abs(self.y - target.y)
    
    def chebyshev_distance(self, target):
        """Chebyshev distance - grid distance (uključuje dijagonale)"""
        return max(abs(self.x - target.x), abs(self.y - target.y))
    
    def distance_to(self, target):
        """Glavni distance method - koristi Chebyshev (grid distance)"""
        return self.chebyshev_distance(target)