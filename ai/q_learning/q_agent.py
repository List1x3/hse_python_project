import numpy as np
from typing import List, Tuple, Dict, Any
from collections import deque
import random
from core.board import Board
from core.game_state import GameState
from ai.q_learning.q_table import QTable

class QAgent:
    def __init__(self, size: int, win_len: int, sym: str = 'O',
                 lr: float = 0.1, gamma: float = 0.9,
                 eps: float = 0.1, eps_decay: float = 0.995,
                 eps_min: float = 0.01, replay: bool = True):
        self.size = size
        self.win_len = win_len
        self.sym = sym
        self.opp = 'X' if sym == 'O' else 'O'
        
        self.lr = lr
        self.gamma = gamma
        self.eps = eps
        self.eps_decay = eps_decay
        self.eps_min = eps_min
        self.replay = replay
        
        self.q = QTable(size, win_len, lr, gamma)
        
        self.buffer = deque(maxlen=10000)
        self.batch = 32
        
        self.last_s = None
        self.last_a = None
        self.hist = []
        
        self.eps_count = 0
        self.total_rew = 0.0
    
    def _possible_acts(self, board: np.ndarray) -> List[int]:
        acts = []
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 0:
                    key = r * self.size + c
                    acts.append(key)
        return acts
    
    def _to_state(self, board: Board, cur_sym: str) -> Tuple[str, np.ndarray]:
        # доска в массив: 0 пусто, 1 X, 2 O
        arr = np.zeros((self.size, self.size), dtype=int)
        
        for r in range(self.size):
            for c in range(self.size):
                cell = board.get_cell(r, c)
                if cell == 'X':
                    arr[r][c] = 1
                elif cell == 'O':
                    arr[r][c] = 2
        
        key = self.q.get_key(arr, cur_sym)
        return key, arr
    
    def choose(self, board: Board, cur_sym: str, 
               train: bool = False) -> Tuple[Tuple[int, int], float]:
        # состояние
        state_key, arr = self._to_state(board, cur_sym)
        # возможные действия
        acts = self._possible_acts(arr)
        
        if not acts:
            return None, 0.0
        if train:
            eps = self.eps
        else:
            eps = 0.0
            
        act_key, val = self.q.best_action(state_key, acts, eps)
        
        # ключ в координаты
        action = self.q.int_to_action(act_key)
        
        # для обучения
        if train:
            self.last_s = state_key
            self.last_a = act_key
        
        return action, val
    
    def reward(self, rew: float, new_board: Board, 
               new_sym: str, done: bool = False) -> None:
        if self.last_s is None or self.last_a is None:
            return
        
        # новое состояние
        new_key, new_arr = self._to_state(new_board, new_sym)
        
        # возможные действия в новом состоянии
        next_acts = []
        if not done:
            next_acts = self._possible_acts(new_arr)
        
        # буфер
        exp = (self.last_s, self.last_a, rew, new_key, next_acts, done)
        
        if self.replay:
            self.buffer.append(exp)
            
            # обучение на случайной выборке
            if len(self.buffer) >= self.batch:
                self._learn()
        else:
            # немедленное обучение
            self.q.update(
                self.last_s,
                self.last_a,
                rew,
                new_key,
                next_acts
            )
        
        # статистика
        self.total_rew += rew
        self.hist.append({
            's': self.last_s,
            'a': self.last_a,
            'r': rew,
            'ns': new_key,
            'done': done
        })
        
        self.last_s = None
        self.last_a = None
        
        # уменьшение epsilon
        if done and self.eps > self.eps_min:
            self.eps *= self.eps_decay
            self.eps = max(self.eps, self.eps_min)
    
    def _learn(self) -> None:
        if len(self.buffer) < self.batch:
            return
        
        batch = random.sample(self.buffer, self.batch)
        
        for exp in batch:
            s, a, r, ns, na, done = exp
            self.q.update(s, a, r, ns, na)
    
    def reset_eps(self) -> None:
        self.last_s = None
        self.last_a = None
        self.eps_count += 1
    
    def save(self, name: str = None) -> str:
        if name is None:
            name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}"
        
        return self.q.save(name)
    
    def load(self, name: str) -> bool:
        return self.q.load(name)
    
    def get_stats(self) -> Dict[str, Any]:
        q_stats = self.q.stats()
        
        return {
            **q_stats,
            'sym': self.sym,
            'eps': self.eps,
            'eps_count': self.eps_count,
            'total_rew': self.total_rew,
            'buffer_size': len(self.buffer),
            'lr': self.lr,
            'gamma': self.gamma
        }
    
    def get_move(self, board: Board, cur_sym: str) -> Dict[str, Any]:
        action, val = self.choose(board, cur_sym, train=False)
        
        if action is None:
            return {
                'action': None,
                'val': 0.0,
                'r': -1,
                'c': -1,
                'conf': 0.0
            }
        
        # уверенность на основе Q значения
        conf = min(1.0, max(0.0, (val + 1) / 2))
        
        return {
            'action': action,
            'val': val,
            'r': action[0],
            'c': action[1],
            'conf': conf
        }
