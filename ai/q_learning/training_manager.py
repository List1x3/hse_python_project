import numpy as np
from typing import Dict, Any
import time
from core.game import Game
from core.game_state import GameState
from ai.q_learning.q_agent import QAgent

class TrainManager:
    def __init__(self, size: int = 3, win_len: int = None, sym: str = 'O'):
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
        
        self.stats = {'eps': 0, 'wins': 0, 'loss': 0, 'draws': 0}
        self.rews = {'win': 1.0, 'lose': -1.0, 'draw': 0.1, 'step': -0.01}
    
    def _calc_win_len(self, size: int, win_len: int) -> int:
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
        start = time.time()
        
        for ep in range(eps):
            game = Game(size=self.size, win_len=self.win_len)
            done = False
            
            while not done:
                cur_board = game.get_board()
                cur_player = game.cur_player.sym
                
                # Проверка на конец игры
                if game.state != GameState.PLAYING:
                    break
                
                if cur_player == self.sym:
                    # Ход ИИ
                    action, _ = self.agent.choose(cur_board, cur_player, train=True)
                    
                    if action is None:
                        # Нет ходов - ничья
                        done = True
                        rew = self.rews['draw']
                        self.stats['draws'] += 1
                        self.agent.reward(rew, cur_board, cur_player, True)
                        break
                    
                    r, c = action
                    if not game.move(r, c):
                        # Некорректный ход
                        done = True
                        break
                    
                    new_board = game.get_board()
                    new_player = game.cur_player.sym
                    
                    # Проверка результата
                    if game.state == GameState.WIN_X:
                        if self.sym == 'X':
                            rew = self.rews['win']
                            self.stats['wins'] += 1
                        else:
                            rew = self.rews['lose']
                            self.stats['loss'] += 1
                        done = True
                    elif game.state == GameState.WIN_O:
                        if self.sym == 'O':
                            rew = self.rews['win']
                            self.stats['wins'] += 1
                        else:
                            rew = self.rews['lose']
                            self.stats['loss'] += 1
                        done = True
                    elif game.state == GameState.DRAW:
                        rew = self.rews['draw']
                        self.stats['draws'] += 1
                        done = True
                    else:
                        rew = self.rews['step']
                    
                    self.agent.reward(rew, new_board, new_player, done)
                
                else:
                    # Ход случайного игрока
                    moves = []
                    for rr in range(self.size):
                        for cc in range(self.size):
                            if cur_board.is_valid(rr, cc):
                                moves.append((rr, cc))
                    
                    if not moves:
                        # Нет ходов - ничья
                        done = True
                        rew = self.rews['draw']
                        self.stats['draws'] += 1
                        # Даем награду ИИ за ничью
                        self.agent.reward(rew, cur_board, cur_player, True)
                        break
                    
                    r, c = moves[np.random.randint(len(moves))]
                    game.move(r, c)
                    
                    # Проверка результата после хода random
                    if game.state == GameState.WIN_X:
                        if self.sym == 'X':
                            rew = self.rews['lose']  # Random выиграл за X
                            self.stats['loss'] += 1
                        else:
                            rew = self.rews['win']   # Random выиграл за O (противник ИИ)
                            self.stats['wins'] += 1
                        done = True
                        # Даем финальную награду ИИ
                        self.agent.reward(rew, game.get_board(), game.cur_player.sym, True)
                    elif game.state == GameState.WIN_O:
                        if self.sym == 'O':
                            rew = self.rews['lose']  # Random выиграл за O
                            self.stats['loss'] += 1
                        else:
                            rew = self.rews['win']   # Random выиграл за X (противник ИИ)
                            self.stats['wins'] += 1
                        done = True
                        self.agent.reward(rew, game.get_board(), game.cur_player.sym, True)
                    elif game.state == GameState.DRAW:
                        rew = self.rews['draw']
                        self.stats['draws'] += 1
                        done = True
                        self.agent.reward(rew, game.get_board(), game.cur_player.sym, True)
            
            self.stats['eps'] += 1
            
            if (ep + 1) % 100 == 0:
                print(f"Эпизод {ep+1}/{eps}: "
                      f"побед={self.stats['wins']}, "
                      f"поражений={self.stats['loss']}, "
                      f"ничьих={self.stats['draws']}")
            
            if (ep + 1) % save_every == 0:
                name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_ep{ep+1}"
                self.agent.save(name)
        
        final_name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_final"
        self.agent.save(final_name)
        
        end = time.time()
        self.stats['time'] = end - start
        print(f"Обучение завершено за {self.stats['time']:.1f} сек")
        
        return self.stats
    
    def get_agent(self) -> QAgent:
        return self.agent
