# ============================================================================
# DATOTEKA: game/map.py
# Uloga: Grid i terrain logika
# ============================================================================

import random
from config.constants import TERRAIN_GRASS, TERRAIN_MOUNTAIN, TERRAIN_WATER

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = self._generate_map()
    
    def _generate_map(self):
        """Generira random mapu s više livade"""
        grid = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                # Random terrain s MNOGO više livade
                rand = random.random()
                if rand < 0.80:  # 80% grass (bilo 65%)
                    terrain = TERRAIN_GRASS
                elif rand < 0.90:  # 10% mountain (bilo 20%)
                    terrain = TERRAIN_MOUNTAIN
                else:  # 10% water (bilo 15%)
                    terrain = TERRAIN_WATER
                
                row.append(terrain)
            grid.append(row)
        
        # Osiguraj da mapa ima dovoljno walkable tile-ova i da je povezana
        self._ensure_playability(grid)
    
        return grid

    def _ensure_playability(self, grid):
        """Osigurava da mapa ima dovoljno prolaznih tile-ova i da su povezani"""
        # 1. Osiguraj minimalno 70% walkable tiles
        walkable_count = sum(
            1 for row in grid for cell in row if cell == TERRAIN_GRASS
        )
        
        total_tiles = self.width * self.height
        min_walkable = int(total_tiles * 0.70)  # Barem 70% walkable
        
        # Ako nema dovoljno walkable, pretvori neke u livadu
        if walkable_count < min_walkable:
            tiles_to_fix = min_walkable - walkable_count
            for y in range(self.height):
                for x in range(self.width):
                    if tiles_to_fix <= 0:
                        break
                    if grid[y][x] != TERRAIN_GRASS:
                        grid[y][x] = TERRAIN_GRASS
                        tiles_to_fix -= 1
        
        # 2. Osiguraj connectivity - flood fill od (0,0)
        self._ensure_connectivity(grid)

    def _ensure_connectivity(self, grid):
        """Osigurava da su sve walkable tile-ove povezane"""
        # Pronađi prvu walkable poziciju
        start_x, start_y = None, None
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == TERRAIN_GRASS:
                    start_x, start_y = x, y
                    break
            if start_x is not None:
                break
        
        if start_x is None:
            return  # Nema walkable tiles (ne bi se trebalo dogoditi)
        
        # Flood fill da nađemo sve dostupne tile-ove
        visited = set()
        stack = [(start_x, start_y)]
        
        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < self.width and 0 <= y < self.height):
                continue
            if grid[y][x] != TERRAIN_GRASS:
                continue
            
            visited.add((x, y))
            
            # Dodaj susjedne tile-ove
            for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                stack.append((x + dx, y + dy))
        
        # Sve walkable tile-ove koje nisu dostupne pretvori u livadu
        # ili napravi puteve do njih
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == TERRAIN_GRASS and (x, y) not in visited:
                    # Ova tile je izolirano - napravi put do nje
                    self._create_path_to(grid, x, y, visited)

    def _create_path_to(self, grid, target_x, target_y, connected_tiles):
        """Stvara put od connected area do target tile-a"""
        # Jednostavna implementacija - napravi direktan put
        # Pronađi najbližu connected tile
        min_dist = float('inf')
        closest = None
        
        for (cx, cy) in connected_tiles:
            dist = abs(target_x - cx) + abs(target_y - cy)
            if dist < min_dist:
                min_dist = dist
                closest = (cx, cy)
        
        if closest is None:
            return
        
        # Napravi put od closest do target
        x, y = closest
        while (x, y) != (target_x, target_y):
            if x < target_x:
                x += 1
            elif x > target_x:
                x -= 1
            elif y < target_y:
                y += 1
            elif y > target_y:
                y -= 1
            
            grid[y][x] = TERRAIN_GRASS
            connected_tiles.add((x, y))
    
    def get_terrain(self, x, y):
        """Vraća tip terena na poziciji"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return None
    
    def is_walkable(self, x, y):
        """Provjerava da li se može hodati na tile"""
        terrain = self.get_terrain(x, y)
        return terrain == TERRAIN_GRASS
    
    def get_random_walkable_position(self, exclude=None):
        """Vraća random walkable poziciju"""
        if exclude is None:
            exclude = []
        
        attempts = 0
        max_attempts = 100
        
        while attempts < max_attempts:
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            
            if self.is_walkable(x, y) and (x, y) not in exclude:
                return (x, y)
            
            attempts += 1
        
        # Fallback - pronađi bilo koju walkable poziciju
        for y in range(self.height):
            for x in range(self.width):
                if self.is_walkable(x, y) and (x, y) not in exclude:
                    return (x, y)
        
        return (0, 0)  # Last resort
