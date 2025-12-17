import random
import time
from datetime import datetime
import json
import os
from pathlib import Path
import numpy as np

from ai.q_learning.q_agent import QAgent
from ai.q_learning.training_manager import TrainManager
from core.board import Board
from core.game import Game
from core.game_state import GameState
from config.paths import get_model_path

class Brain:
    # Кеш загруженных моделей
    _cache = {}
    
    @staticmethod
    def load_model(size, sym):
        # длина для победы по размеру доски
        if size == 3:
            win_len = 3
        elif size == 4:
            win_len = 4
        elif size == 5:
            win_len = 4
        else:
            win_len = 5
        
        # Ключ для кеширования
        key = f"{size}_{sym}"
        
        # Возвращаем из кеша если уже загружена
        if key in Brain._cache:
            return Brain._cache[key]
        
        # агент
        agent = QAgent(size, win_len, sym)
        model_name = f"q_{size}x{size}_win{win_len}_{sym}"
        
        # Пытаемся загрузить модель
        if agent.load(model_name):
            Brain._cache[key] = agent
            return agent
        
        # Если модель не найдена
        return None
    
    @staticmethod
    def think(board_state, size, sym):
        # модель для данного размера и символа
        agent = Brain.load_model(size, sym)
        
        # Если модель не загружена - случайный ход
        if agent is None:
            moves = []
            for r in range(size):
                for c in range(size):
                    if board_state[r][c] == ' ':
                        moves.append((r, c))
            if moves:
                return random.choice(moves)
            return None
        
        # win_len для создания доски
        if size == 3:
            win_len = 3
        elif size == 4:
            win_len = 4
        elif size == 5:
            win_len = 4
        else:
            win_len = 5
        board = Board(size, win_len)
        
        # Заполняем доску из переданного состояния
        for r in range(size):
            for c in range(size):
                cell = board_state[r][c]
                if cell == 'X':
                    board.move(r, c, 'X')
                elif cell == 'O':
                    board.move(r, c, 'O')
        info = agent.get_move(board, sym)
        
        # Если агент вернул ход
        if info['move']:
            return info['move']

        moves = []
        for r in range(size):
            for c in range(size):
                if board_state[r][c] == ' ':
                    moves.append((r, c))
        
        if moves:
            return random.choice(moves)
        
        # Если нет доступных ходов
        return None
    
    @staticmethod
    def get_move(board_state, size, sym):
        # для метода think
        return Brain.think(board_state, size, sym)


class ModelTrainer:
    # Конфигурация обучения для разных размеров досок
    TRAIN_CONFIG = {
        3: {'eps': 5000, 'save': 500, 'win_len': 3},
        4: {'eps': 8000, 'save': 800, 'win_len': 4},
        5: {'eps': 10000, 'save': 1000, 'win_len': 4},
        6: {'eps': 12000, 'save': 1200, 'win_len': 5},
        7: {'eps': 15000, 'save': 1500, 'win_len': 5},
        8: {'eps': 18000, 'save': 1800, 'win_len': 5},
        9: {'eps': 20000, 'save': 2000, 'win_len': 5},
        10: {'eps': 22000, 'save': 2200, 'win_len': 5},
        11: {'eps': 25000, 'save': 2500, 'win_len': 5},
        12: {'eps': 28000, 'save': 2800, 'win_len': 5},
        13: {'eps': 30000, 'save': 3000, 'win_len': 5},
        14: {'eps': 32000, 'save': 3200, 'win_len': 5},
        15: {'eps': 35000, 'save': 3500, 'win_len': 5}
    }
    
    @staticmethod
    def train_one(size, sym='O'):
        # Проверяем наличие конфигурации для данного размера
        if size not in ModelTrainer.TRAIN_CONFIG:
            return
        
        # Получаем конфигурацию
        config = ModelTrainer.TRAIN_CONFIG[size]
        
        # Создаем менеджер обучения
        trainer = TrainManager(
            size=size,
            win_len=config['win_len'],
            sym=sym,
            load_model=False
        )
        
        # Запускаем обучение
        stats = trainer.train_vs_random(
            eps=config['eps'],
            save_every=config['save']
        )
        
        return stats
    
    @staticmethod
    def train_all():
        # время начала обучения
        total_start = time.time()
        all_stats = {}
        
        # Обучаем модели для всех размеров от 3 до 15
        for size in range(3, 16):
            # для символа O
            stats_o = ModelTrainer.train_one(size, 'O')
            all_stats[f"{size}x{size}_O"] = stats_o
            # для символа X
            stats_x = ModelTrainer.train_one(size, 'X')
            all_stats[f"{size}x{size}_X"] = stats_x
        
        # общее время обучения
        total_end = time.time()
        total_time = total_end - total_start
        
        # общая статистика
        summary = {
            'total_time': total_time,
            'total_models': len(all_stats),
            'models': all_stats,
            'completion_time': datetime.now().isoformat()
        }
        
        summary_path = get_model_path("q_learning/training_summary.json")
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return all_stats
    
    @staticmethod
    def train_selected(sizes, syms=None):
        all_stats = {}

        for size in sizes:
            # Пропуск некорректных размеров
            if size < 3 or size > 15:
                continue
            
            # Обучаение для каждого символа
            for sym in syms:
                stats = ModelTrainer.train_one(size, sym)
                all_stats[f"{size}x{size}_{sym}"] = stats
        
        return all_stats
    
    @staticmethod
    def check_models():
        # Проверяем какие модели уже обучены
        models_found = []
        models_missing = []
        
        for size in range(3, 16):
            # Определяем win_len для текущего размера
            win_len = 3 if size == 3 else (4 if size <= 5 else 5)
            
            # Проверяем оба символа
            for sym in ['O', 'X']:
                model_name = f"q_{size}x{size}_win{win_len}_{sym}"
                model_path = get_model_path(f"q_learning/{model_name}.pkl")
                
                # Добавляем в соответствующий список
                if os.path.exists(model_path):
                    models_found.append(f"{size}x{size}_{sym}")
                else:
                    models_missing.append(f"{size}x{size}_{sym}")
        
        return {
            'found': models_found,
            'missing': models_missing
        }

# функции для использования
def get_ai_move(board_state, size, sym):
    # Основная функция для получения хода от ИИ
    return Brain.think(board_state, size, sym)

def train_model(size, sym='O'):
    # Функция для обучения одной модели
    return ModelTrainer.train_one(size, sym)

def train_all_models():
    # Функция для обучения всех моделей
    return ModelTrainer.train_all()

def check_trained_models():
    # Функция для проверки обученных моделей
    return ModelTrainer.check_models()
