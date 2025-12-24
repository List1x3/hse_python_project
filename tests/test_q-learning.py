import pytest
import random
from pathlib import Path
import sys
from ai.q_learning.q_agent import QAgent
from core.board import Board

root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

class TestQ:
    # тесты
    @pytest.mark.parametrize("size,win_len", [
        (3, 3),
        (4, 4),
    ])
    def test_create(self, size, win_len):
        # создание агента
        ag = QAgent(size=size, win_len=win_len, sym='O')
        assert ag.size == size
        assert ag.win_len == win_len
        assert ag.sym == 'O'
    
    @pytest.mark.parametrize("size,win_len", [
        (3, 3),
        (4, 4),
    ])
    def test_empty_board(self, size, win_len):
        # тест с пустой доской
        ag = QAgent(size=size, win_len=win_len, sym='X')
        b = Board(size=size, win_len=win_len)
        m = ag.get_move(b, 'X')
        assert isinstance(m, dict)
        assert 'action' in m
        
        if m['action']:
            r, c = m['action']
            assert 0 <= r < size
            assert 0 <= c < size
            assert b.is_valid(r, c)
    
    @pytest.mark.parametrize("size,win_len", [
        (3, 3),
        (4, 4),
    ])
    def test_partial_board(self, size, win_len):
        # тест с частично заполненной доской
        ag = QAgent(size=size, win_len=win_len, sym='O')
        b = Board(size=size, win_len=win_len)
        for i in range(min(3, size)):
            if b.is_valid(i, i):
                b.move(i, i, 'X' if i % 2 == 0 else 'O')
        m = ag.get_move(b, 'O')
        if m['action']:
            r, c = m['action']
            assert b.is_valid(r, c)
    
    def test_3x3_scenario(self):
        # сценарий для доски 3x3
        ag = QAgent(size=3, win_len=3, sym='O')
        b = Board(size=3, win_len=3)
        
        # позиция с двумя O в ряду
        b.move(0, 0, 'O')
        b.move(0, 1, 'O')
        b.move(1, 0, 'X')
        
        m = ag.get_move(b, 'O')
        if m['action']:
            r, c = m['action']
            assert b.is_valid(r, c)
    
    def test_4x4_scenario(self):
        # сценарий для доски 4x4
        ag = QAgent(size=4, win_len=4, sym='X')
        b = Board(size=4, win_len=4)
        
        # заполненный угол
        b.move(0, 0, 'X')
        b.move(0, 1, 'O')
        b.move(1, 0, 'X')
        
        m = ag.get_move(b, 'X')
        if m['action']:
            r, c = m['action']
            assert b.is_valid(r, c)
    
    @pytest.mark.parametrize("size,win_len", [
        (3, 3),
        (4, 4),
    ])
    def test_learning(self, size, win_len):
        # тест обучения агента
        ag = QAgent(size=size, win_len=win_len, sym='O', eps=0.3)
        b = Board(size=size, win_len=win_len)
        
        # несколько шагов обучения
        for _ in range(5):
            a, _ = ag.choose(b, 'O', train=True)
            if not a:
                break
            
            r, c = a
            b.move(r, c, 'O')
            
            # случайный ответный ход
            if not b.is_game_over():
                empty_cells = [
                    (rr, cc) for rr in range(size) 
                    for cc in range(size) if b.is_valid(rr, cc)
                ]
                if empty_cells:
                    rm = random.choice(empty_cells)
                    b.move(rm[0], rm[1], 'X')
            
            # награда в зависимости от исхода
            w = b.get_winner()
            if w == 'O':
                ag.reward(1.0, b, 'X', done=True)
                break
            elif w == 'X':
                ag.reward(-1.0, b, 'X', done=True)
                break
            elif b.is_full():
                ag.reward(0.1, b, 'X', done=True)
                break
            else:
                ag.reward(-0.01, b, 'X', done=False)
        
        # проверка накопленного опыта
        assert len(ag.buffer) > 0 or ag.q.table
    
    @pytest.mark.parametrize("size,win_len", [
        (3, 3),
        (4, 4),
    ])
    def test_output_format(self, size, win_len):
        # проверка формата ответа агента
        ag = QAgent(size=size, win_len=win_len, sym='X')
        b = Board(size=size, win_len=win_len)
        
        m = ag.get_move(b, 'X')
        
        # обязательные поля в ответе
        assert 'action' in m
        assert 'r' in m
        assert 'c' in m
        assert 'conf' in m
        
        if m['action']:
            assert m['r'] == m['action'][0]
            assert m['c'] == m['action'][1]
            assert 0 <= m['conf'] <= 1
