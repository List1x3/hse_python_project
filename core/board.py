import numpy as np
from typing import List, Tuple, Optional

class Board:
    def __init__(self, size: int = 3, win_len: int = 3):
        # проверки
        if size < 3:
            raise ValueError("size < 3")
        if win_len < 3 or win_len > size:
            raise ValueError(f"win_len 3-{size}")
        
        self.size = size
        self.win_len = win_len
        # 0-пусто, 1-X, 2-O
        self.grid = np.zeros((size, size), dtype=int)
    
    def get_cell(self, r: int, c: int) -> str:
        # вернуть символ
        val = self.grid[r, c]
        if val == 1:
            return 'X'
        elif val == 2:
            return 'O'
        return ' '
    
    def move(self, r: int, c: int, sym: str) -> bool:
        # сделать ход
        if not self.is_valid(r, c):
            return False
        
        val = 1 if sym == 'X' else 2
        self.grid[r, c] = val
        return True
    
    def is_valid(self, r: int, c: int) -> bool:
        # проверить ход
        if r < 0 or r >= self.size or c < 0 or c >= self.size:
            return False
        return self.grid[r, c] == 0
    
    def get_winner(self) -> Optional[str]:
        # найти победителя
        for r in range(self.size):
            for c in range(self.size):
                val = self.grid[r, c]
                if val == 0:
                    continue
                
                sym = 'X' if val == 1 else 'O'
                
                # горизонталь
                if c + self.win_len <= self.size:
                    win = True
                    for i in range(self.win_len):
                        if self.grid[r, c + i] != val:
                            win = False
                            break
                    if win:
                        return sym
                
                # вертикаль
                if r + self.win_len <= self.size:
                    win = True
                    for i in range(self.win_len):
                        if self.grid[r + i, c] != val:
                            win = False
                            break
                    if win:
                        return sym
                
                # диагональ вниз
                if (r + self.win_len <= self.size and 
                    c + self.win_len <= self.size):
                    win = True
                    for i in range(self.win_len):
                        if self.grid[r + i, c + i] != val:
                            win = False
                            break
                    if win:
                        return sym
                
                # диагональ вверх
                if (r - self.win_len + 1 >= 0 and 
                    c + self.win_len <= self.size):
                    win = True
                    for i in range(self.win_len):
                        if self.grid[r - i, c + i] != val:
                            win = False
                            break
                    if win:
                        return sym
        
        return None
    
    def is_full(self) -> bool:
        # проверить заполненность
        return np.all(self.grid != 0)
