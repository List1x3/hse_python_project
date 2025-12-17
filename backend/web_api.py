import random
import os
from pathlib import Path
from flask import Flask, request, jsonify
from ai.q_learning.q_agent import QAgent
from core.board import Board

# путь к файлам моделей
def get_model_path(rel_path: str) -> str:
    # корень проекта
    cur_dir = Path(__file__).parent
    proj_root = cur_dir.parent.parent
    
    # папка для моделей
    mdl_dir = proj_root / "ai" / "models"
    mdl_dir.mkdir(parents=True, exist_ok=True)
    
    # полный путь
    full = mdl_dir / rel_path
    
    # создание папки если нет
    full.parent.mkdir(parents=True, exist_ok=True)
    
    return str(full)

app = Flask(__name__)
_cache = {}

# длина для победы
def win_len(sz):
    if sz == 3: return 3
    elif sz == 4: return 4
    elif sz == 5: return 4
    else: return 5

# получение хода от ИИ
@app.route('/ai/move', methods=['POST'])
def move():
    d = request.json
    
    # проверка данных
    if not d:
        return jsonify({'err': 'нет данных'}), 400
    
    b = d.get('board')
    sz = d.get('size')
    sym = d.get('symbol')
    
    # валидация полей
    if not b or not sz or not sym:
        return jsonify({'err': 'нужны board, size, symbol'}), 400
    
    # проверка размера
    if sz < 3 or sz > 15:
        return jsonify({'err': 'size от 3 до 15'}), 400
    
    # проверка символа
    if sym not in ['X', 'O']:
        return jsonify({'err': 'symbol X или O'}), 400
    
    wl = win_len(sz)
    key = f"{sz}_{sym}"
    
    # загрузка модели если нет в кеше
    if key not in _cache:
        ag = QAgent(sz, wl, sym)
        name = f"q_{sz}x{sz}_win{wl}_{sym}"
        path = get_model_path(f"q_learning/{name}.pkl")
        
        if os.path.exists(path):
            if ag.load(name):
                _cache[key] = ag
    
    # использование модели если загружена
    if key in _cache:
        ag = _cache[key]
        brd = Board(sz, wl)
        
        # заполнение доски
        for r in range(sz):
            for c in range(sz):
                cell = b[r][c]
                if cell == 'X':
                    brd.move(r, c, 'X')
                elif cell == 'O':
                    brd.move(r, c, 'O')
        
        # получение хода
        info = ag.get_move(brd, sym)
        
        if info['action']:
            return jsonify({'r': info['r'], 'c': info['c']})
    
    # случайный ход если нет модели
    mvs = []
    for r in range(sz):
        for c in range(sz):
            if b[r][c] == ' ':
                mvs.append((r, c))
    
    if mvs:
        mv = random.choice(mvs)
        return jsonify({'r': mv[0], 'c': mv[1]})
    
    return jsonify({'err': 'нет ходов'}), 400

# список доступных моделей
@app.route('/ai/models', methods=['GET'])
def models():
    mdl = []
    
    for sz in range(3, 16):
        wl = win_len(sz)
        for sym in ['X', 'O']:
            name = f"q_{sz}x{sz}_win{wl}_{sym}"
            path = get_model_path(f"q_learning/{name}.pkl")
            
            mdl.append({
                'sz': sz,
                'sym': sym,
                'wl': wl,
                'has': os.path.exists(path)
            })
    
    return jsonify({'models': mdl})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
