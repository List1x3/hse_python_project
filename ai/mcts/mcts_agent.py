import numpy as np
import random
import math
from collections import defaultdict
from typing import List, Tuple, Dict, Optional
from core.board import Board

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
    
    def _board_arr_to_str(self, board_arr: np.ndarray) -> str:
        # массив в строку
        return ''.join(str(board_arr[r, c]) for r in range(self.size) for c in range(self.size))
    
    def _state_to_board(self, state: str) -> np.ndarray:
        # строка в массив
        arr = np.zeros((self.size, self.size), dtype=int)
        for idx, char in enumerate(state):
            r = idx // self.size
            c = idx % self.size
            arr[r, c] = int(char)
        return arr
    
    def _check_win(self, board_arr: np.ndarray, r: int, c: int, val: int) -> bool:
        # проверить победу
        if val == 0:
            return False
        
        # горизонталь
        cnt = 1
        for i in range(1, self.win_len):
            if c - i < 0 or board_arr[r, c - i] != val:
                break
            cnt += 1
        for i in range(1, self.win_len):
            if c + i >= self.size or board_arr[r, c + i] != val:
                break
            cnt += 1
        if cnt >= self.win_len:
            return True
        
        # вертикаль
        cnt = 1
        for i in range(1, self.win_len):
            if r - i < 0 or board_arr[r - i, c] != val:
                break
            cnt += 1
        for i in range(1, self.win_len):
            if r + i >= self.size or board_arr[r + i, c] != val:
                break
            cnt += 1
        if cnt >= self.win_len:
            return True
        
        # диагональ /
        cnt = 1
        for i in range(1, self.win_len):
            if r - i < 0 or c - i < 0 or board_arr[r - i, c - i] != val:
                break
            cnt += 1
        for i in range(1, self.win_len):
            if r + i >= self.size or c + i >= self.size or board_arr[r + i, c + i] != val:
                break
            cnt += 1
        if cnt >= self.win_len:
            return True
        
        # диагональ \
        cnt = 1
        for i in range(1, self.win_len):
            if r - i < 0 or c + i >= self.size or board_arr[r - i, c + i] != val:
                break
            cnt += 1
        for i in range(1, self.win_len):
            if r + i >= self.size or c - i < 0 or board_arr[r + i, c - i] != val:
                break
            cnt += 1
        
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
            # проверить победу
            for r in range(self.size):
                for c in range(self.size):
                    val = temp_board[r, c]
                    if val != 0 and self._check_win(temp_board, r, c, val):
                        return 1 if val == 1 else -1
            
            # проверить ничью
            moves = self._get_valid_moves(temp_board)
            if not moves:
                return 0
            
            # случайный ход
            r, c = random.choice(moves)
            temp_board[r, c] = player
            player = 3 - player
    
    def _uct(self, wins: float, visits: int, parent_visits: int) -> float:
        # формула UCT
        if visits == 0:
            return float('inf')
        return (wins / visits) + self.exp_weight * math.sqrt(math.log(parent_visits) / visits)
    
    def get_move(self, board: Board, cur_sym: str) -> Dict:
        # получить ход через MCTS
        board_str = self._board_to_state(board, cur_sym)
        board_arr = self._state_to_board(board_str)
        
        # начальное состояние
        root_key = board_str + '1'
        if root_key not in self.tree:
            self.tree[root_key] = {'visits': 0, 'wins': 0.0, 'moves': {}}
        
        # MCTS цикл
        for _ in range(self.sims):
            # фаза выбора и расширения
            sim_board = board_arr.copy()
            sim_player = 1
            path = []
            state_key = root_key
            
            while True:
                if state_key not in self.tree:
                    self.tree[state_key] = {'visits': 0, 'wins': 0.0, 'moves': {}}
                    break
                
                node = self.tree[state_key]
                moves = self._get_valid_moves(sim_board)
                
                if not moves:
                    break
                
                # найти неисследованные ходы
                unexplored = []
                for move in moves:
                    move_key = f"{move[0]},{move[1]}"
                    if move_key not in node['moves']:
                        unexplored.append(move)
                
                if unexplored:
                    # выбрать случайный неисследованный ход
                    chosen_move = random.choice(unexplored)
                else:
                    # выбрать по UCT
                    best_uct = -float('inf')
                    chosen_move = None
                    
                    for move in moves:
                        move_key = f"{move[0]},{move[1]}"
                        stats = node['moves'][move_key]
                        uct_val = self._uct(stats['wins'], stats['visits'], node['visits'])
                        
                        if uct_val > best_uct:
                            best_uct = uct_val
                            chosen_move = move
                    
                    if chosen_move is None:
                        chosen_move = random.choice(moves)
                
                # записать ход
                move_key = f"{chosen_move[0]},{chosen_move[1]}"
                path.append((state_key, move_key, sim_player))
                
                # сделать ход
                r, c = chosen_move
                sim_board[r, c] = sim_player
                
                # обновить состояние
                sim_player = 3 - sim_player
                new_board_str = self._board_arr_to_str(sim_board)
                state_key = new_board_str + str(sim_player)
            
            # фаза симуляции
            result = self._simulate_random(sim_board, sim_player)
            
            # обратное распространение
            for state_key_back, move_key, player in path:
                node = self.tree[state_key_back]
                node['visits'] += 1
                
                if move_key not in node['moves']:
                    node['moves'][move_key] = {'visits': 0, 'wins': 0.0}
                
                move_stats = node['moves'][move_key]
                move_stats['visits'] += 1
                
                # награда
                reward = result if player == 1 else -result
                if reward > 0:
                    node['wins'] += reward
                    move_stats['wins'] += reward
        
        # выбрать лучший ход
        root = self.tree[root_key]
        moves = self._get_valid_moves(board_arr)
        
        if not moves:
            return {'action': None, 'row': -1, 'col': -1, 'r': -1, 'c': -1, 'conf': 0.0}
        
        best_move = None
        best_visits = -1
        
        for move in moves:
            move_key = f"{move[0]},{move[1]}"
            if move_key in root['moves']:
                visits = root['moves'][move_key]['visits']
                if visits > best_visits:
                    best_visits = visits
                    best_move = move
        
        if best_move is None:
            best_move = random.choice(moves)
        
        conf = min(1.0, best_visits / self.sims) if best_visits > 0 else 0.0
        
        return {
            'action': best_move,
            'row': best_move[0],
            'col': best_move[1],
            'r': best_move[0],
            'c': best_move[1],
            'conf': conf
        }
    
    def reset_tree(self):
        # сбросить дерево
        self.tree.clear()
