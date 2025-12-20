import numpy as np
import random
import math
from collections import defaultdict
from typing import List, Tuple, Dict, Optional
from core.board import Board
from ai.mcts.tree_node import MCTSNode

class MCTSAgent:
    def __init__(self, size: int, win_len: int, sym: str,
                 sims: int = 1000, exp_weight: float = 1.41):
        self.size = size
        self.win_len = win_len
        self.sym = sym
        self.sims = sims
        self.exp_weight = exp_weight
        self.tree = {}
    
    def _board_to_state(self, board: Board, cur_sym: str) -> str:
        # конвертировать доску в строку
        state = []
        for r in range(self.size):
            for c in range(self.size):
                cell = board.get_cell(r, c)
                if cell == cur_sym:
                    state.append('1')
                elif cell == ' ':
                    state.append('0')
                else:
                    state.append('2')
        return ''.join(state)
    
    def _state_to_board(self, state: str, cur_sym: str) -> np.ndarray:
        # строка в массив
        arr = np.zeros((self.size, self.size), dtype=int)
        opp = 'X' if cur_sym == 'O' else 'O'
        
        for idx, char in enumerate(state):
            r = idx // self.size
            c = idx % self.size
            if char == '1':
                arr[r, c] = 1
            elif char == '2':
                arr[r, c] = 2
        
        return arr
    
    def _check_win(self, board_arr: np.ndarray, r: int, c: int, val: int) -> bool:
        # проверить победу
        if val == 0:
            return False
        
        # горизонталь
        cnt = 1
        # влево
        for i in range(1, self.win_len):
            if c - i < 0:
                break
            if board_arr[r, c - i] == val:
                cnt += 1
            else:
                break
        # вправо
        for i in range(1, self.win_len):
            if c + i >= self.size:
                break
            if board_arr[r, c + i] == val:
                cnt += 1
            else:
                break
        if cnt >= self.win_len:
            return True
        
        # вертикаль
        cnt = 1
        # вверх
        for i in range(1, self.win_len):
            if r - i < 0:
                break
            if board_arr[r - i, c] == val:
                cnt += 1
            else:
                break
        # вниз
        for i in range(1, self.win_len):
            if r + i >= self.size:
                break
            if board_arr[r + i, c] == val:
                cnt += 1
            else:
                break
        if cnt >= self.win_len:
            return True
        
        # диагональ
        cnt = 1
        # вверх-влево
        for i in range(1, self.win_len):
            if r - i < 0 or c - i < 0:
                break
            if board_arr[r - i, c - i] == val:
                cnt += 1
            else:
                break
        # вниз-вправо
        for i in range(1, self.win_len):
            if r + i >= self.size or c + i >= self.size:
                break
            if board_arr[r + i, c + i] == val:
                cnt += 1
            else:
                break
        if cnt >= self.win_len:
            return True
        
        # диагональ
        cnt = 1
        # вверх-вправо
        for i in range(1, self.win_len):
            if r - i < 0 or c + i >= self.size:
                break
            if board_arr[r - i, c + i] == val:
                cnt += 1
            else:
                break
        # вниз-влево
        for i in range(1, self.win_len):
            if r + i >= self.size or c - i < 0:
                break
            if board_arr[r + i, c - i] == val:
                cnt += 1
            else:
                break
        
        return cnt >= self.win_len
    
    def _get_valid_moves(self, board_arr: np.ndarray) -> List[Tuple[int, int]]:
        # получить допустимые ходы
        moves = []
        for r in range(self.size):
            for c in range(self.size):
                if board_arr[r, c] == 0:
                    moves.append((r, c))
        return moves
    
    def _simulate_random(self, board_arr: np.ndarray, cur_player: int) -> int:
        # случайная симуляция
        temp_board = board_arr.copy()
        player = cur_player
        
        while True:
            moves = self._get_valid_moves(temp_board)
            if not moves:
                return 0  # ничья
            
            # проверить победу
            board_full = True
            for r in range(self.size):
                for c in range(self.size):
                    if temp_board[r, c] != 0:
                        # проверить победу для этой клетки
                        if self._check_win(temp_board, r, c, temp_board[r, c]):
                            # кто победил
                            return 1 if temp_board[r, c] == 1 else -1
                    else:
                        board_full = False
            
            if board_full:
                return 0
            
            # сделать случайный ход
            r, c = random.choice(moves)
            temp_board[r, c] = player
            player = 3 - player  # переключить 1 2
    
    def _expand_node(self, state: str, board_arr: np.ndarray) -> List[Tuple[int, int]]:
        # расширить узел
        return self._get_valid_moves(board_arr)
    
    def _uct(self, node_wins: float, node_visits: int, parent_visits: int) -> float:
        # формула UCT
        if node_visits == 0:
            return float('inf')
        
        exploit = node_wins / node_visits
        explore = self.exp_weight * math.sqrt(math.log(parent_visits) / node_visits)
        return exploit + explore
    def get_move(self, board: Board, cur_sym: str) -> Dict:
        # получить ход через MCTS
        state_key = self._board_to_state(board, cur_sym)
        board_arr = self._state_to_board(state_key, cur_sym)
    
        # инициализация узла если нет
        if state_key not in self.tree:
            self.tree[state_key] = {
                'visits': 0,
                'wins': 0,
                'moves': {}
            }
    
        root = self.tree[state_key]
    
        # MCTS цикл
        for _ in range(self.sims):
            # ... код симуляции ...
            pass
    
        # выбрать лучший ход
        root_moves = self._get_valid_moves(board_arr)
        if not root_moves:
            return {
                'action': None,
                'r': -1, 'c': -1,
                'row': -1, 'col': -1,
                'conf': 0.0
            }
    
        best_move = None
        best_visits = -1
    
        for move in root_moves:
            move_key = f"{move[0]},{move[1]}"
            if move_key in root['moves']:
                visits = root['moves'][move_key]['visits']
                if visits > best_visits:
                    best_visits = visits
                    best_move = move
    
        if best_move is None:
            best_move = random.choice(root_moves)
    
        return {
            'action': best_move,
            'r': best_move[0],
            'c': best_move[1],
            'row': best_move[0],
            'col': best_move[1],
            'conf': min(1.0, best_visits / self.sims) if best_visits > 0 else 0.0
        }
    
        def reset_tree(self):
            # сбросить дерево
            self.tree.clear()
