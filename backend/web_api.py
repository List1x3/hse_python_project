from flask import Flask, request, jsonify, Blueprint
import random
import os
import shutil
from pathlib import Path
from ai.q_learning.q_agent import QAgent
from core.board import Board
from ai.mcts.mcts_agent import MCTSAgent

# app = Flask(__name__)
_cache = {}  # кеш загруженных моделей

bp = Blueprint('api', __name__)


def get_model_path(rel_path: str) -> str:
    # путь к файлу модели
    cur_dir = Path(__file__).parent
    proj_root = cur_dir.parent.parent

    # папка для моделей
    mdl_dir = proj_root / "ai" / "models" / "q_learning"
    mdl_dir.mkdir(parents=True, exist_ok=True)

    # полный путь
    full = mdl_dir / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)

    return str(full)


def get_models_dir() -> Path:
    # получить папку с моделями
    cur_dir = Path(__file__).parent
    proj_root = cur_dir.parent.parent
    return proj_root / "ai" / "models" / "q_learning"


def prepare_models_for_web():
    # создать копии моделей без _final
    models_dir = get_models_dir()

    if not models_dir.exists():
        print(f"Папка не найдена: {models_dir}")
        return False

    files = list(models_dir.glob("*.pkl"))
    print(f"Найдено моделей: {len(files)}")

    created = 0
    for file in files:
        name = file.stem

        # если это финальная модель
        if name.endswith('_final'):
            # имя без _final
            new_name = name.replace('_final', '')
            new_path = models_dir / f"{new_name}.pkl"

            if not new_path.exists():
                shutil.copy2(file, new_path)
                print(f"Создана копия: {new_name}.pkl")
                created += 1

    print(f"Создано копий: {created}")
    return created > 0


def win_len(sz):
    # длина для победы
    if sz == 3:
        return 3
    elif sz == 4:
        return 4
    elif sz == 5:
        return 4
    else:
        return 5


@bp.route('/ai/move', methods=['POST'])
def ai_move():
    # получить ход от ИИ
    data = request.json

    # проверка данных
    if not data:
        return jsonify({'error': 'нет данных'}), 400

    board = data.get('board')
    print(board)
    size = data.get('size')
    print(size)
    symbol = data.get('symbol')
    print(symbol)

    # валидация полей
    if not board or not size or not symbol:
        return jsonify({'error': 'нужны board, size, symbol'}), 400

    # проверка размера
    if size < 3 or size > 15:
        return jsonify({'error': 'size от 3 до 15'}), 400

    # проверка символа
    if symbol not in ['X', 'O']:
        return jsonify({'error': 'symbol X или O'}), 400

    wl = win_len(size)
    key = f"{size}_{symbol}"

    # загрузка модели если нет в кеше
    if key not in _cache:
        agent = QAgent(size, wl, symbol)

        # имена моделей для поиска
        names_to_try = [
            f"q_{size}x{size}_win{wl}_{symbol}",  # обычная
            f"q_{size}x{size}_win{wl}_{symbol}_final",  # финальная
        ]

        for name in names_to_try:
            path = get_model_path(f"{name}.pkl")
            if os.path.exists(path):
                if agent.load(name):
                    _cache[key] = agent
                    print(f"Загружена модель: {name}")
                    break

    # использование модели если загружена
    if key in _cache:
        agent = _cache[key]
        board_obj = Board(size, wl)

        # заполнение доски
        for r in range(size):
            for c in range(size):
                cell = board[r][c]
                if cell == 'X':
                    board_obj.move(r, c, 'X')
                elif cell == 'O':
                    board_obj.move(r, c, 'O')

        # получение хода
        info = agent.get_move(board_obj, symbol)

        if info['action']:
            return jsonify({
                'row': info['r'], 
                'col': info['c'], 
                'r': info['r'],
                'c': info['c'],
                'confidence': info['conf'],
                'q_value': info['val']
            })

    # случайный ход если нет модели
    moves = []
    for r in range(size):
        for c in range(size):
            if board[r][c] == ' ':
                moves.append((r, c))

    if moves:
        move = random.choice(moves)
        return jsonify({
            'row': move[0],
            'col': move[1],
            'r': move[0],
            'c': move[1],
            'confidence': 0.0
        })

    return jsonify({'error': 'нет ходов'}), 400


@bp.route('/ai/models', methods=['GET'])
def list_models():
    # список доступных моделей
    models = []

    for size in range(3, 16):
        wl = win_len(size)
        for symbol in ['X', 'O']:
            name = f"q_{size}x{size}_win{wl}_{symbol}"
            path = get_model_path(f"{name}.pkl")

            # проверяем обычную и финальную версии
            has_model = os.path.exists(path)
            if not has_model:
                final_path = get_model_path(f"{name}_final.pkl")
                has_model = os.path.exists(final_path)

            models.append({
                'size': size,
                'symbol': symbol,
                'win_len': wl,
                'has_model': has_model
            })

    return jsonify({'models': models})


@bp.route('/ai/health', methods=['GET'])
def health():
    # проверка работы сервера
    return jsonify({'status': 'ok', 'cache_size': len(_cache)})


@bp.route('/ai/clear_cache', methods=['POST'])
def clear_cache():
    # очистить кеш моделей
    _cache.clear()
    return jsonify({'status': 'cache cleared'})


@bp.route('/ai/prepare_models', methods=['POST'])
def prepare_models():
    # подготовить модели для веб-сервера
    try:
        result = prepare_models_for_web()
        return jsonify({'status': 'success', 'prepared': result})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/ai/mcts_move', methods=['POST'])
def mcts_move():
    data = request.json
    
    # проверка данных
    if not data:
        return jsonify({'err': 'нет данных'}), 400
    
    board_state = data.get('board')
    size = data.get('size')
    symbol = data.get('symbol')
    
    # валидация
    if not board_state or not size or not symbol:
        return jsonify({'err': 'нужны board, size, symbol'}), 400
    
    if size < 3 or size > 15:
        return jsonify({'err': 'size от 3 до 15'}), 400
    
    if symbol not in ['X', 'O']:
        return jsonify({'err': 'symbol X или O'}), 400
    
    wl = win_len(size)
    
    # агент
    agent = MCTSAgent(
        size=size,
        win_len=wl,
        sym=symbol,
        sims=1000  # точность
    )
    
    # создать доску
    board = Board(size, wl)
    
    # заполнить доску
    for r in range(size):
        for c in range(size):
            cell = board_state[r][c]
            if cell == 'X':
                board.move(r, c, 'X')
            elif cell == 'O':
                board.move(r, c, 'O')
    
    # ход
    move_info = agent.get_move(board, symbol)

    if move_info:
        row = move_info.get('row') or move_info.get('r')
        col = move_info.get('col') or move_info.get('c')
        
        if row is not None and col is not None:
            response = {
                'row': row,
                'col': col,
                'r': row,
                'c': col,
                'conf': move_info.get('conf', 0.0)
            }
            return jsonify(response)
    
    # резервный случайный ход
    moves = []
    for r in range(size):
        for c in range(size):
            if board_state[r][c] == ' ':
                moves.append((r, c))
    
    if moves:
        mv = random.choice(moves)
        return jsonify({
            'row': mv[0],
            'col': mv[1],
            'r': mv[0],
            'c': mv[1],
            'conf': 0.0
        })
    
    return jsonify({'err': 'нет ходов'}), 400
