from pyswip import Prolog
import os

class PrologAgent:
    def __init__(self):
        self.prolog = Prolog()
        
        # Učitaj Prolog agent
        prolog_file = os.path.join('prolog', 'agent.pl')
        try:
            self.prolog.consult(prolog_file)
            print(f"✓ Prolog agent loaded from {prolog_file}")
        except Exception as e:
            print(f"✗ Error loading Prolog: {e}")
            raise
    
    def get_action(self, game_state):
        """
        Traži od Prolog agenta najbolju akciju
        
        Args:
            game_state: Dictionary s trenutnim stanjem igre
            
        Returns:
            Dictionary s akcijom ili None
        """
        try:
            # Formatiraj game state za Prolog
            prolog_query = self._build_query(game_state)
            
            # Debug print
            # print(f"Prolog query: {prolog_query[:200]}...")  # Print first 200 chars
            
            # Query Prolog za najbolju akciju
            results = list(self.prolog.query(prolog_query, maxresult=1))
            
            if results and len(results) > 0:
                action_term = results[0]['Action']
                # print(f"Prolog returned: {action_term}")
                parsed_action = self._parse_action(action_term, game_state)
                if parsed_action:
                    print(f"  Prolog chose: {parsed_action['type']}")
                return parsed_action
            else:
                print(f"Prolog query returned empty results")
                return None
            
        except Exception as e:
            print(f"Prolog error: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_query(self, state):
        """Gradi Prolog query string"""
        player = state['player']
        enemies = state['enemies']
        terrain = state['terrain']
        actions_left = state['actions_left']
        grid_size = state['grid_size']
        
        # Format player: player(X, Y, HP)
        player_str = f"player({player['x']},{player['y']},{player['hp']})"
        
        # Format enemies: [enemy(Type, X, Y, HP), ...]
        enemy_strs = []
        for e in enemies:
            enemy_type = e['type']
            enemy_strs.append(f"enemy({enemy_type},{e['x']},{e['y']},{e['hp']})")
        enemies_str = "[" + ",".join(enemy_strs) + "]"
        
        # Format terrain: [[0,1,0,...], [2,0,1,...], ...]
        terrain_rows = []
        for row in terrain:
            row_str = "[" + ",".join(str(cell) for cell in row) + "]"
            terrain_rows.append(row_str)
        terrain_str = "[" + ",".join(terrain_rows) + "]"
        
        # Build full query
        game_state_str = f"game_state({player_str},{enemies_str},{terrain_str},{actions_left},{grid_size})"
        query = f"best_action({game_state_str}, Action)"
        
        return query
    
    def _parse_action(self, action_term, game_state):
        """Parsira Prolog akciju u Python dictionary"""
        # action_term je string u formatu: move(3,4) ili melee_attack(2,3,2) itd.
        action_str = str(action_term)
        
        # Parse action type i parametri
        if 'move(' in action_str:
            # Format: move(X, Y)
            params = self._extract_params(action_str)
            if len(params) >= 2:
                return {
                    'type': 'move',
                    'target': (int(params[0]), int(params[1]))
                }
        
        elif 'melee_attack(' in action_str:
            # Format: melee_attack(EnemyX, EnemyY, Damage)
            params = self._extract_params(action_str)
            if len(params) >= 3:
                target_enemy = self._find_enemy_at(
                    int(params[0]), int(params[1]), game_state
                )
                if target_enemy:
                    return {
                        'type': 'melee_attack',
                        'target': target_enemy,
                        'damage': int(params[2])
                    }
        
        elif 'melee_push(' in action_str:
            # Format: melee_push(EnemyX, EnemyY, DX, DY)
            params = self._extract_params(action_str)
            if len(params) >= 4:
                target_enemy = self._find_enemy_at(
                    int(params[0]), int(params[1]), game_state
                )
                if target_enemy:
                    return {
                        'type': 'melee_push',
                        'target': target_enemy,
                        'direction': (int(params[2]), int(params[3]))
                    }
        
        elif 'range_attack(' in action_str:
            # Format: range_attack(EnemyX, EnemyY, Damage)
            params = self._extract_params(action_str)
            if len(params) >= 3:
                target_enemy = self._find_enemy_at(
                    int(params[0]), int(params[1]), game_state
                )
                if target_enemy:
                    return {
                        'type': 'range_attack',
                        'target': target_enemy,
                        'damage': int(params[2])
                    }
        
        elif 'no_action' in action_str:
            return None
        
        print(f"Could not parse action: {action_str}")
        return None
    
    def _extract_params(self, action_str):
        """Ekstraktira parametre iz action string-a"""
        # Extract content between parentheses
        start = action_str.index('(')
        end = action_str.rindex(')')
        params_str = action_str[start+1:end]
        
        # Split by comma
        params = [p.strip() for p in params_str.split(',')]
        return params
    
    def _find_enemy_at(self, x, y, game_state):
        """Pronalazi enemy objekt na zadanoj poziciji iz game_state-a"""
        # NOTE: Ovo vraća dictionary, ne pravi enemy objekt
        # game_loop.py će morati pretraživati svoje actual enemy objekte
        for enemy_data in game_state['enemies']:
            if enemy_data['x'] == x and enemy_data['y'] == y:
                return {'x': x, 'y': y}  # Return position info
        return None