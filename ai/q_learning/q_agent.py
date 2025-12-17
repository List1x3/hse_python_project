import numpy as np
from typing import List, Tuple, Dict
from collections import deque
import random
from core.board import Board
from ai.q_learning.q_table import QTable

class QAgent:
    def __init__(self, size: int, win_len: int, sym: str = 'O',
                 lr: float = 0.1, gamma: float = 0.9,
                 eps: float = 0.1, eps_decay: float = 0.995,
                 eps_min: float = 0.01):
        self.size = size          # размер доски
        self.win_len = win_len    # длина для победы
        self.sym = sym            # символ агента
        self.opp = 'X' if sym == 'O' else 'O'  # противник
        
        self.lr = lr              # скорость обучения
        self.gamma = gamma        # коэффициент дисконтирования
        self.eps = eps            # начальный epsilon
        self.eps_decay = eps_decay  # затухание epsilon
        self.eps_min = eps_min    # минимальный epsilon
        
        self.q = QTable(size, win_len, lr, gamma)  # Q-таблица
        self.buffer = deque(maxlen=10000)  # буфер опыта
        self.batch = 32                     # размер батча
        
        self.last_s = None  # последнее состояние
        self.last_a = None  # последнее действие
    
    def _possible_acts(self, board: np.ndarray) -> List[int]:
        # возвращает список возможных действий
        acts = []
        for r in range(self.size):
            for c in range(self.size):
                if board[r][c] == 0:
                    acts.append(r * self.size + c)
        return acts
    
    def _to_state(self, board: Board, cur_sym: str) -> Tuple[str, np.ndarray]:
        # преобразует доску в состояние
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
        # выбирает действие
        state_key, arr = self._to_state(board, cur_sym)
        acts = self._possible_acts(arr)
        
        if not acts:
            return None, 0.0
            
        eps = self.eps if train else 0.0
        act_key, val = self.q.best_action(state_key, acts, eps)
        
        action = self.q.int_to_action(act_key)
        
        if train:
            self.last_s = state_key
            self.last_a = act_key
        
        return action, val
    
    def reward(self, rew: float, new_board: Board, 
               new_sym: str, done: bool = False) -> None:
        # обрабатывает награду и обучает
        if self.last_s is None or self.last_a is None:
            return
        
        new_key, new_arr = self._to_state(new_board, new_sym)
        next_acts = [] if done else self._possible_acts(new_arr)
        
        exp = (self.last_s, self.last_a, rew, new_key, next_acts, done)
        self.buffer.append(exp)
        
        if len(self.buffer) >= self.batch:
            batch = random.sample(self.buffer, self.batch)
            for s, a, r, ns, na, d in batch:
                self.q.update(s, a, r, ns, na)
        
        if done and self.eps > self.eps_min:
            self.eps *= self.eps_decay
            self.eps = max(self.eps, self.eps_min)
        
        self.last_s = None
        self.last_a = None
    
    def get_move(self, board: Board, cur_sym: str) -> Dict:
        # получает ход для игры (без обучения)
        action, val = self.choose(board, cur_sym, train=False)
        
        if action is None:
            return {'action': None, 'r': -1, 'c': -1}
        
        conf = min(1.0, max(0.0, (val + 1) / 2))
        
        return {
            'action': action,
            'val': val,
            'r': action[0],
            'c': action[1],
            'conf': conf
        }
    
    def save(self, name: str = None) -> str:
        # сохраняет агента
        if name is None:
            name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}"
        return self.q.save(name)
    
    def load(self, name: str) -> bool:
        # загружает агента
        return self.q.load(name)
