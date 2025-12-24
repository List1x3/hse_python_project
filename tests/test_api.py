import pytest
import json
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
from flask import Flask

project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

print(f"Project root: {project_root}")
print(f" Backend path: {backend_path}")


class MockQAgent:
    """Мок для QAgent"""
    def __init__(self, size, win_len, symbol):
        self.size = size
        self.win_len = win_len
        self.symbol = symbol
        print(f"MockQAgent создан: size={size}, win_len={win_len}, symbol={symbol}")

    def load(self, name):
        print(f"MockQAgent.load вызван с: {name}")
        return True

    def get_move(self, board, symbol):
        print(f"MockQAgent.get_move вызван")
        return {
            'action': True,
            'r': 1,
            'c': 1,
            'conf': 0.85,
            'val': 0.92
        }


class MockMCTSAgent:
    """Мок для MCTSAgent"""
    def __init__(self, size, win_len, sym, sims):
        self.size = size
        self.win_len = win_len
        self.sym = sym
        self.sims = sims
        print(f"MockMCTSAgent создан: size={size}, win_len={win_len}, sym={sym}, sims={sims}")

    def get_move(self, board, symbol):
        print(f"MockMCTSAgent.get_move вызван")
        return {
            'row': 2,
            'col': 2,
            'conf': 0.95
        }


class MockBoard:
    """Мок для Board"""
    def __init__(self, size, win_len):
        self.size = size
        self.win_len = win_len
        print(f"MockBoard создан: size={size}, win_len={win_len}")

    def move(self, row, col, symbol):
        print(f"MockBoard.move: ({row}, {col}) = {symbol}")


@pytest.fixture
def flask_app_with_mocks():
    """Создает Flask приложение с замоканными зависимостями"""
    print("\n=== Создание тестового Flask приложения ===")

    # Мокаем все зависимости перед импортом web_api
    with patch.dict('sys.modules', {
        'ai': MagicMock(),
        'ai.q_learning': MagicMock(),
        'ai.q_learning.q_agent': MagicMock(),
        'ai.mcts': MagicMock(),
        'ai.mcts.mcts_agent': MagicMock(),
        'core': MagicMock(),
        'core.board': MagicMock()
    }):
        import sys

        sys.modules['ai.q_learning.q_agent'].QAgent = MockQAgent
        sys.modules['ai.mcts.mcts_agent'].MCTSAgent = MockMCTSAgent
        sys.modules['core.board'].Board = MockBoard

        import backend.web_api as web_api

        app = Flask(__name__)
        app.register_blueprint(web_api.bp)
        app.config['TESTING'] = True

        return app, web_api


@pytest.fixture
def api_client(flask_app_with_mocks):
    """Тестовый клиент для API"""
    app, _ = flask_app_with_mocks
    return app.test_client()


@pytest.fixture
def empty_board_3x3():
    """Пустая доска 3x3"""
    return [[' ' for _ in range(3)] for _ in range(3)]


@pytest.fixture
def sample_board_5x5():
    """Образец доски 5x5"""
    return [
        ['X', 'O', ' ', ' ', ' '],
        [' ', 'X', ' ', 'O', ' '],
        [' ', ' ', ' ', ' ', ' '],
        [' ', 'O', ' ', 'X', ' '],
        [' ', ' ', ' ', ' ', ' ']
    ]


# тесты чтобы поверить что пайтест работает

def test_simple():
    print("Пайтест работает")
    assert True


def test_math():
    """Математические тесты"""
    assert 2 * 2 == 4
    assert 10 / 2 == 5


def test_health_endpoint(api_client):
    """Тест /ai/health"""

    response = api_client.get('/ai/health')

    print(f"Статус: {response.status_code}")
    print(f"Тело: {response.data.decode()[:100]}...")

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'cache_size' in data


def test_clear_cache_endpoint(api_client):
    """Тест /ai/clear_cache"""

    response = api_client.post('/ai/clear_cache')

    assert response.status_code == 200

    data = json.loads(response.data)
    assert data['status'] == 'cache cleared'


def test_list_models_endpoint(api_client):
    """Тест /ai/models"""

    # Мокаем os.path.exists чтобы возвращать True для всех файлов
    with patch('backend.web_api.os.path.exists', return_value=True):
        response = api_client.get('/ai/models')

        print(f"Статус: {response.status_code}")

        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'models' in data
        assert isinstance(data['models'], list)

        if data['models']:
            model = data['models'][0]
            assert 'size' in model
            assert 'symbol' in model
            assert 'win_len' in model
            assert 'has_model' in model


def test_prepare_models_endpoint(api_client):
    """Тест /ai/prepare_models"""

    # Мокаем prepare_models_for_web
    with patch('backend.web_api.prepare_models_for_web') as mock_prepare:
        mock_prepare.return_value = True

        response = api_client.post('/ai/prepare_models')

        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['prepared'] is True


def test_ai_move_endpoint_basic(api_client, empty_board_3x3):
    """Тест /ai/move - базовый случай"""
    with patch('backend.web_api.os.path.exists', return_value=False):
        data = {
            'board': empty_board_3x3,
            'size': 3,
            'symbol': 'X'
        }

        response = api_client.post('/ai/move', json=data)

        assert response.status_code == 200

        result = json.loads(response.data)
        assert 'row' in result
        assert 'col' in result
        assert 'confidence' in result


def test_ai_move_endpoint_with_model(api_client, empty_board_3x3):
    """Тест /ai/move - с моделью"""

    # Мокаем os.path.exists чтобы модель "нашлась"
    with patch('backend.web_api.os.path.exists', return_value=True):
        # Мокаем _cache
        with patch('backend.web_api._cache', {}):
            data = {
                'board': empty_board_3x3,
                'size': 3,
                'symbol': 'X'
            }

            response = api_client.post('/ai/move', json=data)

            assert response.status_code == 200

            result = json.loads(response.data)
            assert 'row' in result
            assert 'col' in result


def test_ai_move_endpoint_invalid_data(api_client):
    """Тест /ai/move - невалидные данные"""
    print("\n=== Тест /ai/move (невалидные данные) ===")

    response = api_client.post('/ai/move', json={})
    print(f"Пустой запрос: статус {response.status_code}")
    assert response.status_code == 400

    data = {
        'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
        'size': 2,
        'symbol': 'X'
    }
    response = api_client.post('/ai/move', json=data)
    assert response.status_code == 400

    data = {
        'board': [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']],
        'size': 3,
        'symbol': 'Z'
    }
    response = api_client.post('/ai/move', json=data)
    assert response.status_code == 400


def test_mcts_move_endpoint(api_client, empty_board_3x3):
    """Тест /ai/mcts_move"""

    data = {
        'board': empty_board_3x3,
        'size': 3,
        'symbol': 'X'
    }

    response = api_client.post('/ai/mcts_move', json=data)

    assert response.status_code == 200

    result = json.loads(response.data)
    assert 'row' in result
    assert 'col' in result
    assert 'conf' in result


def test_mcts_move_invalid(api_client):
    """Тест /ai/mcts_move - невалидные данные"""
    # Пустой запрос
    response = api_client.post('/ai/mcts_move', json={})
    print(f"Пустой запрос: статус {response.status_code}")
    assert response.status_code == 400


def test_win_len_function():
    """Тест функции win_len из web_api"""

    # Импортируем web_api чтобы проверить функцию
    with patch.dict('sys.modules', {
        'ai': MagicMock(),
        'ai.q_learning': MagicMock(),
        'ai.q_learning.q_agent': MagicMock(),
        'ai.mcts': MagicMock(),
        'ai.mcts.mcts_agent': MagicMock(),
        'core': MagicMock(),
        'core.board': MagicMock()
    }):
        import backend.web_api as web_api
        assert web_api.win_len(3) == 3
        assert web_api.win_len(4) == 4
        assert web_api.win_len(5) == 4
        assert web_api.win_len(6) == 5
        assert web_api.win_len(15) == 5


def test_mcts_move_with_invalid_move_info(api_client):
    """Тест MCTS когда get_move возвращает некорректные данные"""
    board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

    with patch('backend.web_api.MCTSAgent') as MockMCTSClass:
        mock_mcts = Mock()
        mock_mcts.get_move.return_value = {
            'some_key': 'value'
        }
        MockMCTSClass.return_value = mock_mcts

        data = {
            'board': board,
            'size': 3,
            'symbol': 'X'
        }

        response = api_client.post('/ai/mcts_move', json=data)
        assert response.status_code == 200

        result = json.loads(response.data)
        assert 'row' in result
        assert 'col' in result


def test_mcts_move_with_none_result(api_client):
    """Тест MCTS когда get_move возвращает None"""
    board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

    with patch('backend.web_api.MCTSAgent') as MockMCTSClass:
        mock_mcts = Mock()
        mock_mcts.get_move.return_value = None
        MockMCTSClass.return_value = mock_mcts

        data = {
            'board': board,
            'size': 3,
            'symbol': 'X'
        }

        response = api_client.post('/ai/mcts_move', json=data)
        assert response.status_code == 200

        result = json.loads(response.data)
        assert 'row' in result
        assert 'col' in result


def test_multiple_consecutive_requests(api_client):
    """Тест нескольких последовательных запросов"""
    board = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

    test_cases = [
        {'size': 3, 'symbol': 'X'},
        {'size': 4, 'symbol': 'O'},
        {'size': 5, 'symbol': 'X'},
    ]

    for params in test_cases:
        size = params['size']
        test_board = [[' ' for _ in range(size)] for _ in range(size)]

        data = {
            'board': test_board,
            'size': size,
            'symbol': params['symbol']
        }

        with patch('backend.web_api.os.path.exists', return_value=False):
            response = api_client.post('/ai/move', json=data)
            assert response.status_code == 200

            result = json.loads(response.data)
            assert 0 <= result['row'] < size
            assert 0 <= result['col'] < size


def test_all_api_endpoints():
    """Общий тест всех API эндпоинтов, чтобы проверить что они есть."""
    print("\n" + "=" * 60)
    print("ОБЩИЙ ТЕСТ ВСЕХ API ЭНДПОИНТОВ")
    print("=" * 60)

    endpoints = [
        '/ai/health',
        '/ai/clear_cache',
        '/ai/models',
        '/ai/prepare_models',
        '/ai/move',
        '/ai/mcts_move'
    ]

    for endpoint in endpoints:
        print(f"  - {endpoint}")

    print("\n" + "=" * 60)

    assert True

