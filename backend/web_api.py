import random
import os
from flask import Flask, request, jsonify
from ai.q_learning.q_agent import QAgent
from core.board import Board
from config.paths import get_model_path

app = Flask(__name__)
_cache = {}  # кеш моделей

def win_len(sz):
    # возвращает длину для победы по размеру
    if sz == 3: return 3
    elif sz == 4: return 4
    elif sz == 5: return 4
    else: return 5

@app.route('/ai/move', methods=['POST'])
def move():
    d = request.json
    
    if not d:
        return jsonify({'err': 'нет данных'}), 400
    
    b = d.get('board')
    sz = d.get('size')
    sym = d.get('symbol')
    
    if not b or not sz or not sym:
        return jsonify({'err': 'нужны board, size, symbol'}), 400
    
    if sz < 3 or sz > 15:
        return jsonify({'err': 'size от 3 до 15'}), 400
    
    if sym not in ['X', 'O']:
        return jsonify({'err': 'symbol X или O'}), 400
    
    wl = win_len(sz)
    key = f"{sz}_{sym}"
    
    if key not in _cache:
        ag = QAgent(sz, wl, sym)
        name = f"q_{sz}x{sz}_win{wl}_{sym}"
        path = get_model_path(f"q_learning/{name}.pkl")
        
        if os.path.exists(path):
            if ag.load(name):
                _cache[key] = ag
    
    if key in _cache:
        ag = _cache[key]
        brd = Board(sz, wl)
        
        for r in range(sz):
            for c in range(sz):
                cell = b[r][c]
                if cell == 'X':
                    brd.move(r, c, 'X')
                elif cell == 'O':
                    brd.move(r, c, 'O')
        
        info = ag.get_move(brd, sym)
        
        if info['action']:
            return jsonify({'r': info['r'], 'c': info['c']})
    
    mvs = []
    for r in range(sz):
        for c in range(sz):
            if b[r][c] == ' ':
                mvs.append((r, c))
    
    if mvs:
        mv = random.choice(mvs)
        return jsonify({'r': mv[0], 'c': mv[1]})
    
    return jsonify({'err': 'нет ходов'}), 400

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
