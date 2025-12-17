import json
import os
import pickle
import numpy as np
from typing import Dict, List, Tuple
from pathlib import Path

class QTable:
    def __init__(self, size: int, win_len: int, lr: float = 0.1, 
                 gamma: float = 0.9, init_val: float = 0.0):
        self.size = size
        self.win_len = win_len
        self.lr = lr
        self.gamma = gamma
        self.init_val = init_val
        self.table: Dict[str, Dict[int, float]] = {}
        self.visits: Dict[str, int] = {}
    
    def get_key(self, board: np.ndarray, symbol: str) -> str:
        # ключ состояния
        board_str = ''.join(str(cell) for row in board for cell in row)
        return f"{board_str}_{symbol}"
    
    def action_to_int(self, action: Tuple[int, int]) -> int:
        r, c = action
        return r * self.size + c
    
    def int_to_action(self, key: int) -> Tuple[int, int]:
        r = key // self.size
        c = key % self.size
        return (r, c)
    
    def get_q(self, state: str, action: int) -> float:
        # получить Q-значение
        if state not in self.table:
            return self.init_val
        return self.table[state].get(action, self.init_val)
    
    def update(self, state: str, action: int, reward: float, 
               next_state: str, next_actions: List[int]) -> None:
        # обновить Q-значение
        cur_q = self.get_q(state, action)
        
        if next_actions:
            max_next = max(self.get_q(next_state, a) for a in next_actions)
        else:
            max_next = 0
        
        new_q = cur_q + self.lr * (reward + self.gamma * max_next - cur_q)
        
        if state not in self.table:
            self.table[state] = {}
        self.table[state][action] = new_q
        
        self.visits[state] = self.visits.get(state, 0) + 1
    
    def best_action(self, state: str, actions: List[int], 
                   eps: float = 0.0) -> Tuple[int, float]:
        # лучший ход (epsilon-greedy)
        if not actions:
            return None, 0.0
            
        if np.random.random() < eps:
            act = np.random.choice(actions)
            return act, self.get_q(state, act)
        
        best_act = None
        best_val = -float('inf')
        
        for act in actions:
            val = self.get_q(state, act)
            if val > best_val:
                best_val = val
                best_act = act
        
        if best_act is None:
            best_act = np.random.choice(actions)
            best_val = self.get_q(state, best_act)
        
        return best_act, best_val
    
    def _get_model_path(self, name: str) -> str:
        # путь к файлу модели
        cur_dir = Path(__file__).parent
        proj_root = cur_dir.parent.parent.parent
        mdl_dir = proj_root / "ai" / "models" / "q_learning"
        mdl_dir.mkdir(parents=True, exist_ok=True)
        return str(mdl_dir / f"{name}.pkl")
    
    def save(self, name: str = None) -> str:
        # сохранить таблицу
        if name is None:
            name = f"q_{self.size}x{self.size}_win{self.win_len}"
        
        data = {
            'size': self.size,
            'win_len': self.win_len,
            'table': self.table,
            'visits': self.visits,
            'lr': self.lr,
            'gamma': self.gamma,
            'init_val': self.init_val
        }
        
        path = self._get_model_path(name)
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        return path
    
    def load(self, name: str) -> bool:
        # загрузить таблицу
        try:
            path = self._get_model_path(name)
            
            if not os.path.exists(path):
                return False
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.table = data.get('table', {})
            self.visits = data.get('visits', {})
            self.lr = data.get('lr', self.lr)
            self.gamma = data.get('gamma', self.gamma)
            self.init_val = data.get('init_val', self.init_val)
            
            return True
            
        except Exception:
            return False
    
    def stats(self) -> Dict:
        # статистика таблицы
        total_states = len(self.table)
        total_acts = sum(len(acts) for acts in self.table.values())
        
        return {
            'states': total_states,
            'actions': total_acts,
            'size': self.size,
            'win_len': self.win_len
        }
