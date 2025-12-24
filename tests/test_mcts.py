import pytest
import numpy as np
import random
import time
from pathlib import Path
import sys

# путь к проекту
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from ai.mcts.mcts_agent import MCTSAgent
from core.board import Board


class TestMCTS:
    # тесты
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (6, 5),
        (7, 5),
        (8, 5),
        (9, 5),
        (10, 5),
    ])
    def test_mcts_create(self, size, win_len):
        # создать агента для размера
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=50)
        assert ag.size == size
        assert ag.win_len == win_len
        assert ag.sym == 'O'
        assert ag.sims == 50
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (6, 5),
        (7, 5),
        (8, 5),  
        (9, 5),
        (10, 5),
    ])
    def test_mcts_empty(self, size, win_len):
        # тест с пустой доской
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=30)
        b = Board(size=size, win_len=win_len)
        
        m = ag.get_move(b, 'X')
        assert isinstance(m, dict)
        
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert 0 <= row < size
            assert 0 <= col < size
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (6, 5),
        (7, 5),
        (8, 5),
        (9, 5),
        (10, 5),
    ])
    def test_mcts_partial(self, size, win_len):
        # тест с частично заполненной доской
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=40)
        b = Board(size=size, win_len=win_len)
        
        # добавить несколько ходов
        cnt = min(5, size)
        for i in range(cnt):
            if b.is_valid(i, i):
                b.move(i, i, 'X' if i % 2 == 0 else 'O')
        
        m = ag.get_move(b, 'O')
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (8, 5),
        (10, 5),
    ])
    def test_mcts_center(self, size, win_len):
        # тест с ходами в центре
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=50)
        b = Board(size=size, win_len=win_len)
        
        # ходы в центре
        center = size // 2
        if b.is_valid(center, center):
            b.move(center, center, 'X')
        if b.is_valid(center, center-1):
            b.move(center, center-1, 'O')
        
        m = ag.get_move(b, 'X')
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (6, 5),
        (9, 5),
    ])
    def test_mcts_corner(self, size, win_len):
        # тест с ходами в углу
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=40)
        b = Board(size=size, win_len=win_len)
        
        # ходы в углу
        if b.is_valid(0, 0):
            b.move(0, 0, 'X')
        if b.is_valid(size-1, size-1):
            b.move(size-1, size-1, 'O')
        
        m = ag.get_move(b, 'O')
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (7, 5),
        (10, 5),
    ])
    def test_mcts_almost_win(self, size, win_len):
        # тест с почти выигрышной позицией
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=60)
        b = Board(size=size, win_len=win_len)
        
        # создать почти выигрышную линию
        line_len = win_len - 1
        for i in range(line_len):
            if b.is_valid(i, i):
                b.move(i, i, 'X')
        
        m = ag.get_move(b, 'X')
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (8, 5),
    ])
    def test_mcts_block(self, size, win_len):
        # тест с блокировкой противника
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=50)
        b = Board(size=size, win_len=win_len)
        
        # противник почти выиграл
        line_len = win_len - 1
        for i in range(line_len):
            if b.is_valid(i, 0):
                b.move(i, 0, 'X')
        
        m = ag.get_move(b, 'O')
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (6, 5),
        (9, 5),
        (10, 5),
    ])
    def test_mcts_speed(self, size, win_len):
        # тест скорости
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=30)
        b = Board(size=size, win_len=win_len)
        
        t1 = time.time()
        m = ag.get_move(b, 'X')
        t2 = time.time()
        
        # должен уложиться в разумное время
        assert t2 - t1 < 5.0
        
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (7, 5),
        (10, 5),
    ])
    def test_mcts_tree_grow(self, size, win_len):
        # рост дерева
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=20)
        b = Board(size=size, win_len=win_len)
        
        s1 = len(ag.tree)
        m1 = ag.get_move(b, 'O')
        s2 = len(ag.tree)
        
        # дерево должно вырасти
        assert s2 > s1
        
        # второй ход на той же доске
        m2 = ag.get_move(b, 'O')
        s3 = len(ag.tree)
        
        # дерево может остаться тем же или вырасти
        assert s3 >= s2
    
    @pytest.mark.parametrize("size,win_len", [
        (5, 4),
        (8, 5),
        (10, 5),
    ])
    def test_mcts_reset(self, size, win_len):
        # сброс дерева
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=20)
        b = Board(size=size, win_len=win_len)
        
        # получить ход
        ag.get_move(b, 'X')
        assert len(ag.tree) > 0
        
        # сбросить
        ag.reset_tree()
        assert len(ag.tree) == 0
        
        # снова получить ход
        m = ag.get_move(b, 'X')
        assert len(ag.tree) > 0
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
    
    @pytest.mark.parametrize("size,win_len", [
        (6, 5),
        (9, 5),
    ])
    def test_mcts_conf(self, size, win_len):
        # уверенность агента
        ag = MCTSAgent(size=size, win_len=win_len, sym='O', sims=40)
        b = Board(size=size, win_len=win_len)
        
        m = ag.get_move(b, 'O')
        if 'conf' in m:
            c = m['conf']
            assert 0 <= c <= 1
    
    @pytest.mark.parametrize("size,win_len", [
        (7, 5),
        (10, 5),
    ])
    def test_mcts_vs_random(self, size, win_len):
        # сравнение mcts и random
        ag = MCTSAgent(size=size, win_len=win_len, sym='X', sims=30)
        b = Board(size=size, win_len=win_len)
        
        # mcts
        t1 = time.time()
        m = ag.get_move(b, 'X')
        t2 = time.time()
        mt = t2 - t1
        
        # random
        t1 = time.time()
        ms = b.get_valid_moves()
        rm = random.choice(ms) if ms else None
        t2 = time.time()
        rt = t2 - t1
        
        # mcts должен думать дольше
        assert mt > rt
        
        # оба валидны
        if m.get('action'):
            row = m.get('row', m.get('r', -1))
            col = m.get('col', m.get('c', -1))
            assert b.is_valid(row, col)
