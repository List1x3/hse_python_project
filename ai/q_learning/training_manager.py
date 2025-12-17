import numpy as np
from typing import Dict, Any, Optional
import time
import json
from datetime import datetime
from pathlib import Path
from core.game import Game
from core.game_state import GameState
from ai.q_learning.q_agent import QAgent
from config.paths import get_model_path

class TrainManager:
    def __init__(self, size: int = 3, win_len: int = None,
                 sym: str = 'O', load_model: bool = False):
        self.size = size
        self.win_len = self._calc_win_len(size, win_len)
        self.sym = sym
        self.opp = 'X' if sym == 'O' else 'O'
        # создаение агента
        self.agent = QAgent(
            size=self.size,
            win_len=self.win_len,
            sym=sym,
            lr=0.1,
            gamma=0.9,
            eps=0.2,
            eps_decay=0.9995,
            eps_min=0.01,
            replay=True
        )
        if load_model:
            name = f"q_{size}x{size}_win{self.win_len}_{sym}"
            if self.agent.load(name):
                print(f"Загружена модель: {name}")
        
        # статистика
        self.stats = {
            'eps': 0,
            'wins': 0,
            'loss': 0,
            'draws': 0,
            'total_rew': 0.0,
            'avg_rew': 0.0,
            'win_rate': 0.0,
            'eps_hist': [],
            'rew_hist': [],
            'start': datetime.now().isoformat()
        }
        
        # награды
        self.rews = {
            'win': 1.0,
            'lose': -1.0,
            'draw': 0.1,
            'step': -0.01,
            'good': 0.05,
            'bad': -0.1
        }
    
    def _calc_win_len(self, size: int, win_len: Optional[int]) -> int:
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
    
    def _eval_move(self, board: Board, r: int, c: int, 
                  sym: str) -> float:
        # проверка ведет ли ход к победе
        temp = Board(self.size, self.win_len)
        temp.board = [row.copy() for row in board.board]
        temp.move(r, c, sym)
        
        if temp.check_win(r, c, sym):
            return 1.0
        
        # проверка на блокировку
        opp = 'X' if sym == 'O' else 'O'
        for rr in range(self.size):
            for cc in range(self.size):
                if temp.is_valid(rr, cc):
                    temp.move(rr, cc, opp)
                    if temp.check_win(rr, cc, opp):
                        return 0.8
                    temp.board[rr][cc] = ' '
        
        # ход в центр
        center = self.size // 2
        if r == center and c == center:
            return 0.3
        
        # ход в угол
        corners = [(0, 0), (0, self.size-1), 
                  (self.size-1, 0), (self.size-1, self.size-1)]
        if (r, c) in corners:
            return 0.2
        
        return 0.0
    
    def train_vs_random(self, eps: int = 1000, save_every: int = 100) -> Dict[str, Any]:
        print(f"Обучение {self.size}x{self.size}, победа: {self.win_len}")
        print(f"Эпизоды: {eps}")
        
        start = time.time()
        
        for ep in range(eps):
            # новая игра
            game = Game(
                size=self.size,
                win_len=self.win_len,
                p1='ai' if self.sym == 'X' else 'human',
                p2='ai' if self.sym == 'O' else 'human'
            )
            
            # сбрасываем агента
            self.agent.reset_eps()
            ep_rew = 0.0
            done = False
            
            while not done:
                cur_board = game.get_board()
                cur_player = game.cur_player
                
                # ход агента
                if cur_player.sym == self.sym:
                    action, _ = self.agent.choose(
                        cur_board, cur_player.sym, train=True
                    )
                    
                    if action is None:
                        break
                    
                    r, c = action
                    game.move(r, c)
                    
                    # новое состояние
                    new_board = game.get_board()
                    new_player = game.cur_player
                    
                    # оценка хода
                    move_q = self._eval_move(cur_board, r, c, self.sym)
                    step_rew = self.rews['step']
                    
                    # результат
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
                        rew = step_rew + move_q * self.rews['good']
                    
                    # награда
                    self.agent.reward(
                        rew, new_board, new_player.sym, done
                    )
                    
                    ep_rew += rew
                
                # ход случайного оппонента
                else:
                    moves = []
                    for rr in range(self.size):
                        for cc in range(self.size):
                            if cur_board.is_valid(rr, cc):
                                moves.append((rr, cc))
                    
                    if moves:
                        r, c = moves[np.random.randint(len(moves))]
                        game.move(r, c)
            
            # статистика
            self.stats['eps'] += 1
            self.stats['total_rew'] += ep_rew
            self.stats['rew_hist'].append(ep_rew)
            self.stats['eps_hist'].append(self.agent.eps)
            
            # прогресс
            if (ep + 1) % 100 == 0:
                wins = self.stats['wins']
                total = self.stats['eps']
                rate = wins / total if total > 0 else 0
                
                print(f"Эпизод {ep + 1}/{eps} | "
                      f"Победы: {wins} ({rate:.1%}) | "
                      f"Eps: {self.agent.eps:.3f}")
            
            # сохранение
            if (ep + 1) % save_every == 0:
                name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_ep{ep+1}"
                self.agent.save(name)
                
                self._save_stats()
        
        # финальное сохранение
        final_name = f"q_{self.size}x{self.size}_win{self.win_len}_{self.sym}_final"
        self.agent.save(final_name)
        
        # финальная статистика
        end = time.time()
        train_time = end - start
        
        self.stats['time'] = train_time
        self.stats['end'] = datetime.now().isoformat()
        
        if self.stats['eps'] > 0:
            self.stats['avg_rew'] = (
                self.stats['total_rew'] / self.stats['eps']
            )
            self.stats['win_rate'] = (
                self.stats['wins'] / self.stats['eps']
            )
        
        self._save_stats()
        
        print(f"\nОбучение завершено: {train_time:.1f} сек")
        print(f"Эпизодов: {self.stats['eps']}")
        print(f"Побед: {self.stats['wins']} ({self.stats['win_rate']:.1%})")
        print(f"Проигрышей: {self.stats['loss']}")
        print(f"Ничьих: {self.stats['draws']}")
        print(f"Средняя награда: {self.stats['avg_rew']:.3f}")
        
        return self.stats
    
    def _save_stats(self) -> None:
        path = get_model_path(
            f"q_learning/stats/train_{self.size}x{self.size}_"
            f"win{self.win_len}_{self.sym}.json"
        )
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def load_stats(self) -> Optional[Dict[str, Any]]:
        path = get_model_path(
            f"q_learning/stats/train_{self.size}x{self.size}_"
            f"win{self.win_len}_{self.sym}.json"
        )
        
        if Path(path).exists():
            with open(path, 'r') as f:
                return json.load(f)
        
        return None
    
    def evaluate(self, games: int = 100) -> Dict[str, Any]:
        print(f"Оценка на {games} играх...")
        
        res = {
            'wins': 0,
            'loss': 0,
            'draws': 0,
            'rate': 0.0,
            'avg_moves': 0.0,
            'games': []
        }
        
        total_moves = 0
        
        for g in range(games):
            game = Game(
                size=self.size,
                win_len=self.win_len,
                p1='ai' if self.sym == 'X' else 'human',
                p2='ai' if self.sym == 'O' else 'human'
            )
            
            moves = 0
            result = None
            
            while game.state == GameState.IN_PROGRESS:
                cur_board = game.get_board()
                cur_player = game.cur_player
                
                # ход агента
                if cur_player.sym == self.sym:
                    action, _ = self.agent.choose(
                        cur_board, cur_player.sym, train=False
                    )
                    
                    if action is None:
                        break
                    
                    r, c = action
                    game.move(r, c)
                    moves += 1
                
                # ход случайного
                else:
                    valid = []
                    for rr in range(self.size):
                        for cc in range(self.size):
                            if cur_board.is_valid(rr, cc):
                                valid.append((rr, cc))
                    
                    if valid:
                        r, c = valid[np.random.randint(len(valid))]
                        game.move(r, c)
                        moves += 1
                    else:
                        break
            
            # результат
            if game.state == GameState.WIN_X and self.sym == 'X':
                res['wins'] += 1
                result = 'win'
            elif game.state == GameState.WIN_O and self.sym == 'O':
                res['wins'] += 1
                result = 'win'
            elif game.state == GameState.WIN_X and self.sym == 'O':
                res['loss'] += 1
                result = 'loss'
            elif game.state == GameState.WIN_O and self.sym == 'X':
                res['loss'] += 1
                result = 'loss'
            else:
                res['draws'] += 1
                result = 'draw'
            
            total_moves += moves
            res['games'].append({
                'num': g + 1,
                'res': result,
                'moves': moves
            })
            
            # прогресс
            if (g + 1) % 20 == 0:
                print(f"  Игр: {g + 1}/{games}")
        
        # итоговая статистика
        res['rate'] = res['wins'] / games if games > 0 else 0
        res['avg_moves'] = total_moves / games if games > 0 else 0
        
        print(f"\nРезультаты:")
        print(f"  Побед: {res['wins']} ({res['rate']:.1%})")
        print(f"  Поражений: {res['loss']}")
        print(f"  Ничьих: {res['draws']}")
        print(f"  Средние ходы: {res['avg_moves']:.1f}")
        
        return res
    
    def get_agent(self) -> QAgent:
        return self.agent
