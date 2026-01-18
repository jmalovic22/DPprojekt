# ============================================================================
# DATOTEKA: game/turn_manager.py
# Uloga: Upravlja turn-ovima
# ============================================================================

class TurnManager:
    def __init__(self):
        self.current_turn = "player"  # "player" ili "enemies"
        self.actions_left = 2  # Player ima 2 akcije po turn-u
        self.turn_number = 1
    
    def next_turn(self):
        """Prelazi na sljedeći turn"""
        if self.current_turn == "player":
            self.current_turn = "enemies"
            self.actions_left = self._get_enemy_actions()
        else:
            self.current_turn = "player"
            self.actions_left = 2
            self.turn_number += 1
    
    def _get_enemy_actions(self):
        """Vraća broj akcija za enemy turn"""
        # Range enemy ima 1, melee ima 2
        # Za jednostavnost, ovdje vraćamo ukupan broj
        # U game_loop.py se svaki enemy izvršava zasebno
        return 3  # 1 za range + 2 za melee
    
    def use_action(self):
        """Koristi jednu akciju"""
        self.actions_left = max(0, self.actions_left - 1)
    
    def get_current_entity(self):
        """Vraća koji entitet je trenutno na potezu"""
        return self.current_turn
    
    def reset_enemy_actions(self, enemies):
        """Resetuje acted_this_turn flag za sve neprijatelje"""
        for enemy in enemies:
            enemy.acted_this_turn = False