import numpy as np
from typing import Dict, Any
import time
from pathlib import Path
from core.game import Game
from core.game_state import GameState
from ai.q_learning.q_agent import QAgent
from config.paths import get_model_path

class TrainManager:
    def __init__(self, size: int = 3, win_len: int = None,
                 sym: str = 'O'):
        self.size = size
        self.win_len = self._calc_win_len(size, win_len)
        self.sym = sym
        
        self.agent = QAgent(
            size=self.size,
            win_len=self.win_len,
            sym=sym,
            lr=0.1,
            gamma=0.9,
            eps=0.2,
            eps_decay=0.9995,
            eps_min=0.01
        )
        
        self.stats = {
            'eps': 0,
            'wins': 0,
            'loss': 0,
            'draws': 0
        }
        
        self.rews = {
            'win': 1.0,
            'lose': -1.0,
            'draw': 0.1,
            'step': -0.01
        }
    
    def _calc_win_len(self, size: int, win_len: int) -> int:
        # вычисляет длину для победы
        if win_len is not None:
            return win_len
        
        if size == 3:
            return 3
        elif size == 4:
            return 4
        elif size == 5:
            return 4
        else:
            return 5
    
    def train_vs_random(self, eps: int = 1000, save_every: int = 100) -> Dict[str, Any]:
        # обучает агента против случайного соперника
        start = time.time()
        
        for ep in range(eps):
            game = Game(
                size=self.size,
                win_len=self.win_len,
                p1='ai' if self.sym == 'X' else 'human',
                p2='ai' if self.sym == 'O' else 'human'
            )
            
            done = False
            
            while not done:
                cur_board = game.get_board()
                cur_player = game.cur_player
                
                if cur_player.sym == self.sym:
                    action, _ = self.agent.choose(cur_board, cur_player.sym, train=True)
                    
                    if action is None:
                        break
                    
                    r, c = action
                    game.move(r, c)
                    
                    new_board = game.get_board()
                    new_player = game.cur_player
                    
                    if game.state == GameState.WIN_X and self.sym == 'X':
                        rew = self.rews['win']
                        done = True
                        self.stats['wins'] += 1
                    elif game.state == GameState.WIN_O and self.sym == 'O':
                        rew = self.rews['win']
                        done = True
                        self.stats['wins'] += 1
                    elif game.state == GameState.WIN_X and self.sym == 'O':
                        rew = self.rews['lose']
                        done = True
                        self.stats['loss'] += 1
                    elif game.state == GameState.WIN_O and self.sym == 'X':
                        rew = self.rews['lose']
                        done = True
                        self.stats['loss'] += 1
                    elif game.state == GameState.DRAW:
                        rew = self.rews['draw']
                        done = True
                        self.stats['draws'] += 1
                    else:
                        rew = self.rews['step']
                    
                    self.agent.reward(rew, new_board, new_player.sym, done)
                
                else:
                    moves = []
                    for rr in range(self.size):
                        for cc in range(self.size):
                            if cur_board.is_valid(rr, cc):
                                moves.append((rr, cc))
                    
                    if moves:
                        r, c = moves[np.random.randint(len(moves))]
                        game.move(r, c)
            
            self.stats['eps'] += 1
            
            if (ep + 1) % save_every == 0:
                name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_ep{ep+1}"
                self.agent.save(name)
        
        final_name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_final"
        self.agent.save(final_name)
        
        end = time.time()
        self.stats['time'] = end - start
        
        return self.stats
    
    def get_agent(self) -> QAgent:
        return self.agent
