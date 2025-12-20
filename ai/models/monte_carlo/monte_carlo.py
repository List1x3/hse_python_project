import numpy as np
import random
from collections import defaultdict
import time
from typing import List, Tuple, Optional
import math

class TicTacToe:
    def __init__(self, board_size: int = 3):
        self.board_size = board_size
        self.board = np.zeros((board_size, board_size), dtype=int)
        self.current_player = 1  # 1 для крестиков, -1 для ноликов
        self.win_length = self._get_win_length(board_size)
        self.game_over = False
        self.winner = 0
        
    def _get_win_length(self, size: int) -> int:
        """Определяет длину линии для победы в зависимости от размера поля"""
        if size == 3:
            return 3
        elif size == 4:
            return 4
        elif size == 5:
            return 4
        else:
            return min(5, size)  # Для 6x6 и больше - 5 в ряд
    
    def reset(self):
        """Сброс игры"""
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.game_over = False
        self.winner = 0
    
    def get_valid_moves(self) -> List[Tuple[int, int]]:
        """Возвращает список возможных ходов"""
        if self.game_over:
            return []
        
        moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves
    
    def make_move(self, row: int, col: int) -> bool:
        """Сделать ход"""
        if self.game_over or self.board[row][col] != 0:
            return False
        
        self.board[row][col] = self.current_player
        
        # Проверка на победу
        if self.check_win(row, col):
            self.game_over = True
            self.winner = self.current_player
        # Проверка на ничью
        elif len(self.get_valid_moves()) == 0:
            self.game_over = True
            self.winner = 0
        else:
            self.current_player *= -1
            
        return True
    
    def check_win(self, row: int, col: int) -> bool:
        """Проверка победы после последнего хода"""
        player = self.board[row][col]
        
        # Проверка по горизонтали
        count = 1
        # Влево
        for c in range(col-1, max(-1, col-self.win_length), -1):
            if self.board[row][c] == player:
                count += 1
            else:
                break
        # Вправо
        for c in range(col+1, min(self.board_size, col+self.win_length)):
            if self.board[row][c] == player:
                count += 1
            else:
                break
        
        if count >= self.win_length:
            return True
        
        # Проверка по вертикали
        count = 1
        # Вверх
        for r in range(row-1, max(-1, row-self.win_length), -1):
            if self.board[r][col] == player:
                count += 1
            else:
                break
        # Вниз
        for r in range(row+1, min(self.board_size, row+self.win_length)):
            if self.board[r][col] == player:
                count += 1
            else:
                break
        
        if count >= self.win_length:
            return True
        
        # Проверка по диагонали (лево-верх -> право-низ)
        count = 1
        # Лево-верх
        r, c = row-1, col-1
        while r >= 0 and c >= 0 and count < self.win_length:
            if self.board[r][c] == player:
                count += 1
                r -= 1
                c -= 1
            else:
                break
        # Право-низ
        r, c = row+1, col+1
        while r < self.board_size and c < self.board_size and count < self.win_length:
            if self.board[r][c] == player:
                count += 1
                r += 1
                c += 1
            else:
                break
        
        if count >= self.win_length:
            return True
        
        # Проверка по диагонали (право-верх -> лево-низ)
        count = 1
        # Право-верх
        r, c = row-1, col+1
        while r >= 0 and c < self.board_size and count < self.win_length:
            if self.board[r][c] == player:
                count += 1
                r -= 1
                c += 1
            else:
                break
        # Лево-низ
        r, c = row+1, col-1
        while r < self.board_size and c >= 0 and count < self.win_length:
            if self.board[r][c] == player:
                count += 1
                r += 1
                c -= 1
            else:
                break
        
        return count >= self.win_length
    
    def get_state_key(self) -> str:
        """Получить строковое представление состояния"""
        return str(self.board.tobytes()) + str(self.current_player)
    
    def print_board(self):
        """Вывести доску в консоль"""
        symbols = {0: '.', 1: 'X', -1: 'O'}
        
        print("\n   " + " ".join(str(i) for i in range(self.board_size)))
        for i in range(self.board_size):
            row_str = f"{i}: "
            for j in range(self.board_size):
                row_str += symbols[self.board[i][j]] + " "
            print(row_str)
        print()


class MCTSAgent:
    def __init__(self, board_size: int, player: int, exploration_weight: float = 1.41):
        self.board_size = board_size
        self.player = player  # 1 или -1
        self.exploration_weight = exploration_weight
        self.Q = defaultdict(float)  # Сумма наград для состояния-действия
        self.N = defaultdict(int)   # Количество посещений для состояния-действия
        self.Ns = defaultdict(int)  # Количество посещений для состояния
        
    def get_action(self, game: TicTacToe, num_simulations: int = 1000) -> Tuple[int, int]:
        """Выбрать действие с помощью MCTS"""
        valid_moves = game.get_valid_moves()
        
        if not valid_moves:
            return None
        
        # Если это первый ход, можно использовать эвристику для скорости
        if len(valid_moves) == game.board_size * game.board_size:
            # Первый ход - обычно в центр или ближе к нему
            center = game.board_size // 2
            if (center, center) in valid_moves:
                return (center, center)
            else:
                return random.choice(valid_moves)
        
        # UCT поиск
        for _ in range(num_simulations):
            self._simulate(game)
        
        state_key = game.get_state_key()
        
        # Выбираем действие с максимальным значением Q/N
        best_move = None
        best_value = -float('inf')
        
        for move in valid_moves:
            action_key = (state_key, move)
            if self.N[action_key] > 0:
                value = self.Q[action_key] / self.N[action_key]
            else:
                value = 0
            
            if value > best_value:
                best_value = value
                best_move = move
        
        # Если лучший ход не найден (все действия не исследованы), выбираем случайный
        if best_move is None:
            best_move = random.choice(valid_moves)
        
        return best_move
    
    def _simulate(self, game: TicTacToe):
        """Одна симуляция MCTS"""
        # Копируем игру для симуляции
        sim_game = TicTacToe(game.board_size)
        sim_game.board = np.copy(game.board)
        sim_game.current_player = game.current_player
        sim_game.game_over = game.game_over
        sim_game.winner = game.winner
        
        visited_states = []
        
        # Фаза выбора и расширения
        while not sim_game.game_over:
            state_key = sim_game.get_state_key()
            valid_moves = sim_game.get_valid_moves()
            
            # Если есть неисследованные действия
            unexplored_moves = []
            for move in valid_moves:
                action_key = (state_key, move)
                if self.N[action_key] == 0:
                    unexplored_moves.append(move)
            
            if unexplored_moves:
                # Выбираем случайное неисследованное действие
                move = random.choice(unexplored_moves)
                action_key = (state_key, move)
                
                # Запоминаем состояние и действие
                visited_states.append(action_key)
                
                # Делаем ход
                sim_game.make_move(*move)
                break
            else:
                # Выбираем действие по UCB1
                best_ucb = -float('inf')
                best_move = None
                
                for move in valid_moves:
                    action_key = (state_key, move)
                    exploitation = self.Q[action_key] / self.N[action_key]
                    exploration = self.exploration_weight * math.sqrt(
                        math.log(self.Ns[state_key]) / self.N[action_key]
                    )
                    ucb = exploitation + exploration
                    
                    if ucb > best_ucb:
                        best_ucb = ucb
                        best_move = move
                
                if best_move:
                    action_key = (state_key, best_move)
                    visited_states.append(action_key)
                    sim_game.make_move(*best_move)
        
        # Фаза симуляции (случайные ходы до конца игры)
        self._rollout(sim_game)
        
        # Фаза обратного распространения
        reward = self._get_reward(sim_game)
        
        for action_key in visited_states:
            self.Q[action_key] += reward
            self.N[action_key] += 1
            
            state_key, _ = action_key
            self.Ns[state_key] += 1
    
    def _rollout(self, game: TicTacToe):
        """Случайная симуляция до конца игры"""
        while not game.game_over:
            valid_moves = game.get_valid_moves()
            if valid_moves:
                move = random.choice(valid_moves)
                game.make_move(*move)
            else:
                break
    
    def _get_reward(self, game: TicTacToe) -> float:
        """Получить награду для текущего игрока"""
        if game.winner == 0:
            return 0.5  # Ничья
        elif game.winner == self.player:
            return 1.0  # Победа
        else:
            return 0.0  # Поражение


class RandomAgent:
    """Случайный агент для тестирования"""
    def __init__(self, player: int):
        self.player = player
    
    def get_action(self, game: TicTacToe, **kwargs) -> Tuple[int, int]:
        valid_moves = game.get_valid_moves()
        return random.choice(valid_moves) if valid_moves else None


def train_agent(board_size: int = 3, num_games: int = 1000, simulations_per_move: int = 500):
    """Обучение агента методом Монте-Карло"""
    print(f"Обучение на поле {board_size}x{board_size}...")
    print(f"Количество игр: {num_games}")
    print(f"Симуляций на ход: {simulations_per_move}")
    
    # Создаем агентов
    agent_x = MCTSAgent(board_size, player=1)
    agent_o = MCTSAgent(board_size, player=-1)
    
    # Статистика
    stats = {'X_wins': 0, 'O_wins': 0, 'draws': 0}
    
    for game_num in range(num_games):
        if (game_num + 1) % 100 == 0:
            print(f"Игра {game_num + 1}/{num_games}")
        
        # Создаем новую игру
        game = TicTacToe(board_size)
        
        # Случайно выбираем, кто начинает (для баланса)
        if random.random() < 0.5:
            current_agent = agent_x
        else:
            current_agent = agent_o
            game.current_player = -1
        
        # Играем игру
        while not game.game_over:
            # Получаем ход от текущего агента
            if current_agent.player == 1:
                move = agent_x.get_action(game, num_simulations=simulations_per_move)
            else:
                move = agent_o.get_action(game, num_simulations=simulations_per_move)
            
            if move:
                game.make_move(*move)
            
            # Переключаем агента
            current_agent = agent_o if current_agent == agent_x else agent_x
        
        # Обновляем статистику
        if game.winner == 1:
            stats['X_wins'] += 1
        elif game.winner == -1:
            stats['O_wins'] += 1
        else:
            stats['draws'] += 1
    
    # Выводим статистику
    print("\nСтатистика обучения:")
    print(f"Побед X: {stats['X_wins']} ({stats['X_wins']/num_games*100:.1f}%)")
    print(f"Побед O: {stats['O_wins']} ({stats['O_wins']/num_games*100:.1f}%)")
    print(f"Ничьих: {stats['draws']} ({stats['draws']/num_games*100:.1f}%)")
    
    return agent_x, agent_o


def play_against_ai(board_size: int = 3, agent: MCTSAgent = None, 
                   simulations_per_move: int = 1000):
    """Игра против обученного AI"""
    if agent is None:
        print("Создаю нового агента...")
        agent = MCTSAgent(board_size, player=1)
    
    game = TicTacToe(board_size)
    human_player = 1  # Человек играет крестиками
    ai_player = -1    # AI играет ноликами
    
    print(f"\nИгра против AI на поле {board_size}x{board_size}")
    print(f"Для победы нужно {game.win_length} в ряд")
    print("Вы играете крестиками (X)")
    print("Введите ход в формате 'ряд столбец' (например: '1 2')")
    
    while not game.game_over:
        game.print_board()
        
        if game.current_player == human_player:
            # Ход человека
            valid_moves = game.get_valid_moves()
            
            while True:
                try:
                    move_input = input("Ваш ход: ").strip()
                    if move_input.lower() == 'выход':
                        return
                    
                    coords = list(map(int, move_input.split()))
                    if len(coords) != 2:
                        print("Введите 2 числа через пробел")
                        continue
                    
                    move = (coords[0], coords[1])
                    if move in valid_moves:
                        break
                    else:
                        print("Недопустимый ход. Попробуйте снова.")
                except ValueError:
                    print("Введите числа")
                except KeyboardInterrupt:
                    return
            
            game.make_move(*move)
        else:
            # Ход AI
            print("AI думает...")
            move = agent.get_action(game, num_simulations=simulations_per_move)
            
            if move:
                print(f"AI ходит: {move[0]} {move[1]}")
                game.make_move(*move)
    
    # Конец игры
    game.print_board()
    
    if game.winner == human_player:
        print("Поздравляю! Вы победили!")
    elif game.winner == ai_player:
        print("AI победил!")
    else:
        print("Ничья!")


def test_agents(board_size: int = 3, num_games: int = 100, 
                agent1_simulations: int = 500, agent2_simulations: int = 500):
    """Тестирование двух агентов друг против друга"""
    print(f"\nТестирование на поле {board_size}x{board_size}")
    print(f"Количество игр: {num_games}")
    
    agent1 = MCTSAgent(board_size, player=1, exploration_weight=1.41)
    agent2 = MCTSAgent(board_size, player=-1, exploration_weight=1.41)
    
    stats = {'agent1_wins': 0, 'agent2_wins': 0, 'draws': 0}
    
    for game_num in range(num_games):
        game = TicTacToe(board_size)
        
        # Чередуем, кто начинает
        if game_num % 2 == 0:
            current_agent = agent1
        else:
            current_agent = agent2
            game.current_player = -1
        
        while not game.game_over:
            if current_agent.player == 1:
                move = agent1.get_action(game, num_simulations=agent1_simulations)
            else:
                move = agent2.get_action(game, num_simulations=agent2_simulations)
            
            if move:
                game.make_move(*move)
            
            current_agent = agent2 if current_agent == agent1 else agent1
        
        if game.winner == 1:
            stats['agent1_wins'] += 1
        elif game.winner == -1:
            stats['agent2_wins'] += 1
        else:
            stats['draws'] += 1
    
    print("\nРезультаты тестирования:")
    print(f"Побед агента 1 (X): {stats['agent1_wins']} ({stats['agent1_wins']/num_games*100:.1f}%)")
    print(f"Побед агента 2 (O): {stats['agent2_wins']} ({stats['agent2_wins']/num_games*100:.1f}%)")
    print(f"Ничьих: {stats['draws']} ({stats['draws']/num_games*100:.1f}%)")


def main():
    """Главная функция"""
    print("Крестики-нолики с обучением методом Монте-Карло")
    print("=" * 50)
    
    while True:
        print("\nМеню:")
        print("1. Обучить агента")
        print("2. Играть против AI")
        print("3. Тестировать агентов друг против друга")
        print("4. Выход")
        
        choice = input("Выберите опцию: ").strip()
        
        if choice == "1":
            # Обучение агента
            try:
                board_size = int(input("Размер поля (3-10): ").strip())
                if not (3 <= board_size <= 10):
                    print("Размер должен быть от 3 до 10")
                    continue
                
                num_games = int(input("Количество игр для обучения (рекомендуется 1000-5000): ").strip())
                simulations = int(input("Симуляций на ход (рекомендуется 500-2000): ").strip())
                
                agent_x, agent_o = train_agent(board_size, num_games, simulations)
                
                # Предлагаем сыграть против обученного агента
                play = input("\nХотите сыграть против обученного AI? (да/нет): ").strip().lower()
                if play == 'да':
                    play_against_ai(board_size, agent_o, min(simulations, 1000))
            
            except ValueError:
                print("Ошибка ввода. Пожалуйста, введите числа.")
        
        elif choice == "2":
            # Игра против AI
            try:
                board_size = int(input("Размер поля (3-10): ").strip())
                if not (3 <= board_size <= 10):
                    print("Размер должен быть от 3 до 10")
                    continue
                
                simulations = int(input("Симуляций на ход AI (рекомендуется 1000-5000): ").strip())
                
                # Создаем агента с базовыми знаниями
                agent = MCTSAgent(board_size, player=-1)
                play_against_ai(board_size, agent, simulations)
            
            except ValueError:
                print("Ошибка ввода. Пожалуйста, введите числа.")
        
        elif choice == "3":
            # Тестирование агентов
            try:
                board_size = int(input("Размер поля (3-10): ").strip())
                if not (3 <= board_size <= 10):
                    print("Размер должен быть от 3 до 10")
                    continue
                
                num_games = int(input("Количество игр для тестирования: ").strip())
                sims1 = int(input("Симуляций на ход для агента 1: ").strip())
                sims2 = int(input("Симуляций на ход для агента 2: ").strip())
                
                test_agents(board_size, num_games, sims1, sims2)
            
            except ValueError:
                print("Ошибка ввода. Пожалуйста, введите числа.")
        
        elif choice == "4":
            print("Выход из программы")
            break
        
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()