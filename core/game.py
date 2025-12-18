from .board import Board
from .game_state import GameState
from typing import Tuple, Optional

class Player:
    def __init__(self, sym: str):
        self.sym = sym

class Game:
    def __init__(self, size: int = 3, win_len: int = 3, 
                 p1: str = 'human', p2: str = 'human'):
        self.board = Board(size, win_len)
        self.players = {
            'X': Player('X'),
            'O': Player('O')
        }
        self.cur_player = self.players['X']
        self.state = GameState.PLAYING
    
    def get_board(self) -> Board:
        # получить доску
        return self.board
    
    def move(self, r: int, c: int) -> bool:
        # сделать ход
        if self.state != GameState.PLAYING:
            return False
        
        if not self.board.move(r, c, self.cur_player.sym):
            return False
        
        # проверить состояние
        winner = self.board.get_winner()
        if winner == 'X':
            self.state = GameState.WIN_X
        elif winner == 'O':
            self.state = GameState.WIN_O
        elif self.board.is_full():
            self.state = GameState.DRAW
        else:
            self.state = GameState.PLAYING
        
        # сменить игрока
        if self.state == GameState.PLAYING:
            next_sym = 'O' if self.cur_player.sym == 'X' else 'X'
            self.cur_player = self.players[next_sym]
        
        return True
        
    def is_game_over(self) -> bool:
        # Проверить, закончилась ли игра
        return self.state != GameState.PLAYING
