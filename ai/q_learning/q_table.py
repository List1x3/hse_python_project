import json
import os
import pickle
import numpy as np
from typing import Dict, List, Tuple
from config.paths import get_model_path

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
        # доска в виде строки + символ игрока
        board_str = ''.join(str(cell) for row in board for cell in row)
        return f"{board_str}_{symbol}"
    
    def action_to_int(self, action: Tuple[int, int]) -> int:
        row, col = action
        return row * self.size + col
    
    def int_to_action(self, key: int) -> Tuple[int, int]:
        row = key // self.size
        col = key % self.size
        return (row, col)
    
    def get_q(self, state: str, action: int) -> float:
        if state not in self.table:
            return self.init_val
        return self.table[state].get(action, self.init_val)
    
    def get_all_q(self, state: str) -> Dict[int, float]:
        if state not in self.table:
            return {}
        return self.table[state].copy()
    
    def update(self, state: str, action: int, reward: float, 
               next_state: str, next_actions: List[int]) -> None:
        # текущее Q значение
        cur_q = self.get_q(state, action)
        
        # максимальное Q для следующего состояния
        if next_actions:
            max_next = max(self.get_q(next_state, a) for a in next_actions)
        else:
            max_next = 0
        
        # формула Q-learning
        new_q = cur_q + self.lr * (reward + self.gamma * max_next - cur_q)
        
        # обновление таблицы
        if state not in self.table:
            self.table[state] = {}
        self.table[state][action] = new_q
        
        # счетчик посещений
        self.visits[state] = self.visits.get(state, 0) + 1
    
    def best_action(self, state: str, actions: List[int], 
                   eps: float = 0.0) -> Tuple[int, float]:
        if not actions:
            return None, 0.0
            
        # случайное исследование
        if np.random.random() < eps:
            act = np.random.choice(actions)
            val = self.get_q(state, act)
            return act, val
        
        # жадный выбор
        best_act = None
        best_val = -float('inf')
        
        for act in actions:
            val = self.get_q(state, act)
            if val > best_val:
                best_val = val
                best_act = act
        
        # если все значения равны начальным
        if best_act is None or best_val == self.init_val:
            best_act = np.random.choice(actions)
            best_val = self.get_q(state, best_act)
        
        return best_act, best_val
    
    def save(self, name: str = None) -> str:
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
        
        path = get_model_path(f"q_learning/{name}.pkl")
        
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        
        # метаданные
        meta = {
            'size': self.size,
            'win_len': self.win_len,
            'states': len(self.table),
            'lr': self.lr,
            'gamma': self.gamma,
            'total_visits': sum(self.visits.values())
        }
        
        meta_path = get_model_path(f"q_learning/{name}_meta.json")
        with open(meta_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        return path
    
    def load(self, name: str) -> bool:
        try:
            path = get_model_path(f"q_learning/{name}.pkl")
            
            if not os.path.exists(path):
                return False
            
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            # проверка совместимости
            if data['size'] != self.size or data['win_len'] != self.win_len:
                print(f"Внимание: параметры модели не совпадают")
            
            self.table = data.get('table', {})
            self.visits = data.get('visits', {})
            self.lr = data.get('lr', self.lr)
            self.gamma = data.get('gamma', self.gamma)
            self.init_val = data.get('init_val', self.init_val)
            
            print(f"Загружена таблица: {len(self.table)} состояний")
            return True
            
        except Exception as e:
            print(f"Ошибка загрузки: {e}")
            return False
    
    def stats(self) -> Dict:
        total_states = len(self.table)
        total_acts = sum(len(acts) for acts in self.table.values())
        total_vis = sum(self.visits.values())
        
        avg_acts = total_acts / total_states if total_states > 0 else 0
        
        return {
            'states': total_states,
            'actions': total_acts,
            'visits': total_vis,
            'avg_acts': avg_acts,
            'size': self.size,
            'win_len': self.win_len
        }
    
    def clear(self) -> None:
        self.table.clear()
        self.visits.clear()
