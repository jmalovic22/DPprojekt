# ============================================================================
# DATOTEKA: config/constants.py
# Uloga: Game settings i konstante
# ============================================================================

# Screen settings
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Grid settings
GRID_SIZE = 6
TILE_SIZE = 80
GRID_OFFSET_X = 50
GRID_OFFSET_Y = 50

# Terrain types
TERRAIN_GRASS = 0
TERRAIN_MOUNTAIN = 1
TERRAIN_WATER = 2

# Colors
COLOR_BG = (40, 40, 50)
COLOR_GRASS = (100, 180, 100)
COLOR_MOUNTAIN = (120, 120, 120)
COLOR_WATER = (80, 120, 200)
COLOR_GRID_LINE = (60, 60, 70)

COLOR_PLAYER = (50, 150, 255)
COLOR_ENEMY_RANGE = (255, 100, 100)
COLOR_ENEMY_MELEE = (200, 50, 50)

COLOR_TEXT = (255, 255, 255)
COLOR_PAUSE = (255, 255, 100)
COLOR_WIN = (100, 255, 100)
COLOR_LOSE = (255, 100, 100)

# Game settings
TURN_DELAY = 1.5  # Sekunde između turn-ova

# Player settings
PLAYER_HP = 5
PLAYER_ACTIONS = 2

# Enemy settings
RANGE_ENEMY_HP = 3
MELEE_ENEMY_HP = 4