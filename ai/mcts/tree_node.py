from typing import Dict, Any, List, Tuple, Optional

class MCTSNode:
    def __init__(self, state: str = ""):
        self.state = state
        self.visits = 0
        self.wins = 0.0
        self.moves: Dict[str, Dict[str, Any]] = {}
        self.children: Dict[str, 'MCTSNode'] = {}
    
    def add_move(self, move_key: str):
        # добавить ход
        if move_key not in self.moves:
            self.moves[move_key] = {'visits': 0, 'wins': 0}
    
    def update_move(self, move_key: str, reward: float):
        # обновить статистику хода
        if move_key in self.moves:
            self.moves[move_key]['visits'] += 1
            self.moves[move_key]['wins'] += reward
        self.visits += 1
        self.wins += reward
    
    def best_move(self, exp_weight: float = 1.41) -> Optional[str]:
        # лучший ход по UCT
        import math
        
        if not self.moves:
            return None
        
        best_key = None
        best_score = -float('inf')
        
        for move_key, stats in self.moves.items():
            if stats['visits'] == 0:
                score = float('inf')
            else:
                exploit = stats['wins'] / stats['visits']
                explore = exp_weight * math.sqrt(math.log(self.visits) / stats['visits'])
                score = exploit + explore
            
            if score > best_score:
                best_score = score
                best_key = move_key
        
        return best_key
    
    def most_visited_move(self) -> Optional[str]:
        # самый посещаемый ход
        if not self.moves:
            return None
        
        best_key = None
        best_visits = -1
        
        for move_key, stats in self.moves.items():
            if stats['visits'] > best_visits:
                best_visits = stats['visits']
                best_key = move_key
        
        return best_key
