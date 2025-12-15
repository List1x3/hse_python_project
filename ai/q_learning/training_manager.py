import time
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from core.board import Board
from .q_agent import QAgent

class Trainer:
    # обучает агентов
    def __init__(self, path="models/q_learning"):
        self.path = Path(path)
        self.path.mkdir(parents=True, exist_ok=True)
        # настройки
        self.games = 20000
        self.n = 3
        self.lr = 0.1
        self.gamma = 0.9
        self.eps = 0.2
        self.eps_down = 0.995
        self.eps_min = 0.01
        # награды
        self.win = 1.0
        self.lose = -1.0
        self.draw = 0.5
        # статистика
        self.s = {
            'g': [],  # игры
            'x': [],  # победы X
            'o': [],  # победы O
            'd': [],  # ничьи
            'e': [],  # eps
            't': []   # размер таблицы
        }
        # агенты
        self.x = None
        self.o = None

    def make_agents(self):
        # создает агентов
        from .q_table import QTable
        table = QTable(board_size=self.n, lr=self.lr, gamma=self.gamma)
        self.x = QAgent(
            sym='X',
            size=self.n,
            q_table=table,
            eps=self.eps,
            lr=self.lr,
            gamma=self.gamma,
            eps_reduce=self.eps_down,
            eps_min=self.eps_min
        )

        self.o = QAgent(
            sym='O',
            size=self.n,
            q_table=table,
            eps=self.eps,
            lr=self.lr,
            gamma=self.gamma,
            eps_reduce=self.eps_down,
            eps_min=self.eps_min
        )

    def play_one(self) -> str:
        # одна игра
        board = Board(size=self.n)
        x_first = np.random.random() > 0.5
        self.x.reset()
        self.o.reset()

        while not board.game_over:
            if ((board.current_player == 'X' and x_first) or 
                (board.current_player == 'O' and not x_first)):
                a = self.x
                b = self.o
            else:
                a = self.o
                b = self.x

            r, c = a.get_move(board, train=True)
            board.make_move(r, c, a.sym)
            reward = 0
            done = board.game_over
            if done:
                if board.winner == a.sym:
                    reward = self.win
                    other_r = self.lose
                elif board.winner is None:
                    reward = self.draw
                    other_r = self.draw
                else:
                    reward = self.lose
                    other_r = self.win
                a.update(reward, board, done)
                b.update(other_r, board, done)
            else:
                a.update(reward, board, done)

        return board.winner

    def train(self):
        # обучение
        self.make_agents()
        print(f"Обучение: {self.games} игр, доска {self.n}×{self.n}")
        start = time.time()

        for g in range(self.games):
            winner = self.play_one()
            self.x.reduce_eps()
            self.o.reduce_eps()
            self._update(g, winner)
            if (g + 1) % 1000 == 0:
                print(f"Игра {g+1}: X={self.s['x'][-1]:.1%}, "
                      f"O={self.s['o'][-1]:.1%}, eps={self.x.eps:.3f}")
            if (g + 1) % 5000 == 0:
                self.save(f"model_{self.n}x{self.n}_{g+1}")

        self.save(f"model_{self.n}x{self.n}_final")
        t = time.time() - start

    def _update(self, g: int, winner: str):
        # обновляет статистику
        win_x = 1.0 if winner == 'X' else 0.0
        win_o = 1.0 if winner == 'O' else 0.0
        win_d = 1.0 if winner is None else 0.0

        if not self.s['g']:
            # первая игра
            self.s['g'].append(g + 1)
            self.s['x'].append(win_x)
            self.s['o'].append(win_o)
            self.s['d'].append(win_d)
            self.s['e'].append(self.x.eps)
            self.s['t'].append(self.x.q.size())
        else:
            # среднее
            window = min(100, g + 1)
            start = max(0, len(self.s['x']) - window + 1)
            avg_x = np.mean(self.s['x'][start:] + [win_x])
            avg_o = np.mean(self.s['o'][start:] + [win_o])
            avg_d = np.mean(self.s['d'][start:] + [win_d])
            self.s['g'].append(g + 1)
            self.s['x'].append(avg_x)
            self.s['o'].append(avg_o)
            self.s['d'].append(avg_d)
            self.s['e'].append(self.x.eps)
            self.s['t'].append(self.x.q.size())

    def save(self, name: str):
        # сохраняет модель
        path = self.path / f"{name}.pkl"
        self.x.save(str(path))
        cfg = {
            'n': self.n,
            'games': self.games,
            'lr': self.lr,
            'gamma': self.gamma,
            'eps': self.eps,
            'eps_down': self.eps_down,
            'eps_min': self.eps_min
        }
        cfg_path = self.path / f"{name}_cfg.json"
        with open(cfg_path, 'w') as f:
            json.dump(cfg, f, indent=2)
