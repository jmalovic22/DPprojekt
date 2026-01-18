from collections import deque
from config.constants import TERRAIN_GRASS, GRID_SIZE

def find_path_bfs(start_x, start_y, target_x, target_y, game_map, occupied_positions):
    """
    BFS pathfinding - nalazi najkraći put od start do target
    
    Args:
        start_x, start_y: početna pozicija
        target_x, target_y: ciljna pozicija
        game_map: GameMap objekt
        occupied_positions: lista pozicija koje su zauzete [(x,y), ...]
    
    Returns:
        Sljedeća pozicija (x, y) prema cilju, ili None ako nema puta
    """
    if start_x == target_x and start_y == target_y:
        return None
    
    # BFS
    queue = deque([(start_x, start_y, [])])  # (x, y, path)
    visited = {(start_x, start_y)}
    
    while queue:
        x, y, path = queue.popleft()
        
        # Provjeri sve susjedne pozicije (4-directional)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            
            # Skip ako je izvan granica
            if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
                continue
            
            # Skip ako je već posjećeno
            if (nx, ny) in visited:
                continue
            
            # Skip ako je terrain neprohodan
            if not game_map.is_walkable(nx, ny):
                continue
            
            # Skip ako je pozicija zauzeta (osim target pozicije)
            if (nx, ny) in occupied_positions and (nx, ny) != (target_x, target_y):
                continue
            
            # Novi path
            new_path = path + [(nx, ny)]
            
            # Ako smo stigli do cilja, vrati prvi korak
            if nx == target_x and ny == target_y:
                if new_path:
                    return new_path[0]
                return None
            
            # Dodaj u queue
            queue.append((nx, ny, new_path))
            visited.add((nx, ny))
    
    # Nema puta do cilja
    return None


def get_next_move_towards(entity, target, game_map, occupied_positions):
    """
    Helper funkcija - vraća sljedeći move prema targetu koristeći pathfinding
    
    Args:
        entity: entitet koji se kreće
        target: cilj (mora imati .x i .y)
        game_map: GameMap objekt
        occupied_positions: lista zauzenih pozicija
    
    Returns:
        Tuple (x, y) sljedeće pozicije ili None
    """
    next_pos = find_path_bfs(
        entity.x, entity.y,
        target.x, target.y,
        game_map,
        occupied_positions
    )
    
    return next_pos


def get_next_move_away_from(entity, threat, game_map, occupied_positions, max_search=10):
    """
    Nalazi move koji se udaljava od threat-a
    
    Args:
        entity: entitet koji se kreće
        threat: prijetnja od koje bježimo
        game_map: GameMap objekt
        occupied_positions: lista zauzenih pozicija
        max_search: maksimalna dubina pretraživanja
    
    Returns:
        Tuple (x, y) sljedeće pozicije ili None
    """
    current_dist = max(abs(entity.x - threat.x), abs(entity.y - threat.y))
    
    best_move = None
    best_distance = current_dist
    
    # Provjeri sve susjedne pozicije (samo 4-directional)
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        nx, ny = entity.x + dx, entity.y + dy
        
        # Skip ako je izvan granica
        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            continue
        
        # Skip ako je terrain neprohodan
        if not game_map.is_walkable(nx, ny):
            continue
        
        # Skip ako je pozicija zauzeta
        if (nx, ny) in occupied_positions:
            continue
        
        # Izračunaj novu distance od threat-a
        new_dist = max(abs(nx - threat.x), abs(ny - threat.y))
        
        # Ako je dalje nego trenutna pozicija, to je dobar kandidat
        if new_dist > best_distance:
            best_distance = new_dist
            best_move = (nx, ny)
    
    return best_move