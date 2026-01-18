# ============================================================================
# DATOTEKA: main.py
# Uloga: Entry point - pokreće cijelu igru
# ============================================================================

import pygame
from game_loop import GameLoop

def main():
    """Pokreće igru"""
    pygame.init()
    
    game = GameLoop()
    game.run()
    
    pygame.quit()

if __name__ == "__main__":
    main()
