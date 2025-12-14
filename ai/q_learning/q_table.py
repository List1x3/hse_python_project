import pickle
import numpy as np
from typing import Dict, List

class QTable:
    # хранит q значения для состояний игры
    
    def __init__(self, board_size=3, lr=0.1, gamma=0.9):
        self.size = board_size
        self.table: Dict[str, List[float]] = {}  # q таблица
        self.lr = lr  # скорость обучения
        self.gamma = gamma  # кэффициент награды
        self.cache = {}  # кэш состояний

    def norm_state(self, state_str: str) -> str:
        # Приводит состояние к стандартному виду
        if state_str in self.cache:
            return self.cache[state_str]

        n = self.size
        matrix = [list(state_str[i * n:(i + 1) * n]) for i in range(n)]

        # Все повороты и отражения
        all_states = []
        for _ in range(4):
            all_states.append(matrix)
            matrix = [list(row) for row in zip(*matrix[::-1])]

        # Минимальная строка
        min_str = None
        for m in all_states:
            s = ''.join([''.join(row) for row in m])
            if min_str is None or s < min_str:
                min_str = s

        self.cache[state_str] = min_str
        return min_str

    def get_key(self, state: str, player: str) -> str:
        # Ключ для состояния
        return f"{self.size}_{self.norm_state(state)}_{player}"

    def get_q(self, key: str) -> List[float]:
        # q значения для состояния
        if key not in self.table:
            self.table[key] = [0.0] * (self.size * self.size)
        return self.table[key]

    def best_move(self, key: str, moves: List[int], eps=0.0) -> int:
        # Лучший ход или случайный с вероятностью eps
        q_vals = self.get_q(key)
        valid_q = [(i, q_vals[i]) for i in moves]

        if np.random.random() < eps:
            return np.random.choice(moves) if moves else -1

        # Лучший по q
        if valid_q:
            best = max(valid_q, key=lambda x: x[1])
            same = [m for m, q in valid_q if abs(q - best[1]) < 0.001]
            return np.random.choice(same) if len(same) > 1 else best[0]

        return -1

    def update(self, key: str, action: int, reward: float, next_key: str, done: bool):
        # обновляет q таблицу
        q_vals = self.get_q(key)
        current = q_vals[action]

        if done:
            target = reward
        else:
            next_q = self.get_q(next_key)
            max_next = max(next_q) if next_q else 0
            target = reward + self.gamma * max_next

        # Формула q-learning
        q_vals[action] = current + self.lr * (target - current)
        self.table[key] = q_vals

    def save(self, path: str):
        # сохраняет таблицу
        with open(path, 'wb') as f:
            pickle.dump({
                'size': self.size,
                'table': self.table,
                'lr': self.lr,
                'gamma': self.gamma,
                'cache': self.cache
            }, f)

    def load(self, path: str):
        # загружает таблицу
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.size = data['size']
            self.table = data['table']
            self.lr = data.get('lr', 0.1)
            self.gamma = data.get('gamma', 0.9)
            self.cache = data.get('cache', {})

    def size(self) -> int:
        # количество состояний
        return len(self.table)
