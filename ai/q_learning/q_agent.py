import numpy as np
from typing import Tuple, Optional
from core.board import Board
from .q_table import QTable


class QAgent:
    # агент q learning

    def __init__(self,
                 symbol: str,          # X или O
                 size: int = 3,        # размер доски n
                 q_table: Optional[QTable] = None,
                 eps: float = 0.1,     # вероятность случайного хода
                 lr: float = 0.1,      # скорость обучения
                 gamma: float = 0.9,   # коэффициент награды
                 eps_reduce: float = 0.995,  # уменьшение eps после игры
                 eps_min: float = 0.01):     # минимальный eps

        self.sym = symbol      # символ игрока
        self.size = size       # размер доски

        # параметры обучения
        self.eps = eps         # вероятность случайного хода
        self.lr = lr           # скорость обучения
        self.gamma = gamma     # важность будущих наград
        self.eps_reduce = eps_reduce  # насколько уменьшать eps
        self.eps_min = eps_min  # минимальное значение eps

        # q таблица
        self.q = q_table or QTable(board_size=size, lr=lr, gamma=gamma)

        # для обучения
        self.last_key = None   # ключ последнего состояния
        self.last_act = None   # последнее действие
        self.last_state = None # последнее состояние

    def get_move(self, board: Board, train: bool = False) -> Tuple[int, int]:
        # выбирает ход
        state = board.get_state_key()
        key = self.q.get_key(state, self.sym)

        # доступные ходы
        moves = board.get_available_moves()
        idxs = [r * self.size + c for (r, c) in moves]

        if not idxs:
            return -1, -1

        # eps для исследования
        cur_eps = self.eps if train else 0.0

        # выбор действия
        act = self.q.best_move(key, idxs, cur_eps)

        # если нет лучшего - случайный
        if act == -1 and idxs:
            act = np.random.choice(idxs)

        # для обучения
        if train:
            self.last_key = key
            self.last_act = act
            self.last_state = state

        # индекс в координаты
        row = act // self.size
        col = act % self.size

        return row, col

    def update(self, reward: float, next_board: Board, done: bool):
        # обновляет q таблицу
        if self.last_key is None:
            return

        next_state = next_board.get_state_key()
        next_key = self.q.get_key(next_state, self.sym)

        self.q.update(
            key=self.last_key,
            action=self.last_act,
            reward=reward,
            next_key=next_key,
            done=done
        )

        self.reset()

    def reduce_eps(self):
        # уменьшает eps (после игры)
        self.eps = max(self.eps_min, self.eps * self.eps_reduce)

    def reset(self):
        # сбрасывает временные данные
        self.last_key = None
        self.last_act = None
        self.last_state = None

    def save(self, path: str):
        # сохраняет агента (q таблицу)
        self.q.save(path)

    def load(self, path: str):
        # загружает агента
        self.q.load(path)
