import pytest
import json
from unittest.mock import patch, MagicMock
from flask import Flask
import sys
import os


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # корень

print(f"\n=== DEBUG: sys.path настроен ===")
print(f"Текущая директория: {os.getcwd()}")
print(f"sys.path: {sys.path[:3]}...")


# Создаем полные моки для всех зависимостей
mock_ai = MagicMock()
mock_q_learning = MagicMock()
mock_q_agent = MagicMock()
mock_mcts = MagicMock()
mock_mcts_agent = MagicMock()
mock_core = MagicMock()
mock_board = MagicMock()

mock_ai.q_learning = mock_q_learning
mock_ai.q_learning.q_agent = mock_q_agent
mock_ai.mcts = mock_mcts
mock_ai.mcts.mcts_agent = mock_mcts_agent


# мок классы
class MockQAgent:
    def __init__(self, *args, **kwargs):
        pass

    def load(self, name):
        return True

    def get_move(self, board, symbol):
        return {'action': True, 'r': 1, 'c': 1, 'conf': 0.8, 'val': 0.9}


class MockMCTSAgent:
    def __init__(self, *args, **kwargs):
        pass

    def get_move(self, board, symbol):
        return {'row': 2, 'col': 2, 'conf': 0.95}


class MockBoard:
    def __init__(self, *args, **kwargs):
        pass

    def move(self, *args, **kwargs):
        pass


# Присваиваем классы
mock_q_agent.QAgent = MockQAgent
mock_mcts_agent.MCTSAgent = MockMCTSAgent
mock_board.Board = MockBoard
mock_core.board = mock_board

# Заменяем в sys.modules
sys.modules['ai'] = mock_ai
sys.modules['ai.q_learning'] = mock_q_learning
sys.modules['ai.q_learning.q_agent'] = mock_q_agent
sys.modules['ai.mcts'] = mock_mcts
sys.modules['ai.mcts.mcts_agent'] = mock_mcts_agent
sys.modules['core'] = mock_core
sys.modules['core.board'] = mock_board


try:
    import importlib

    with patch.dict('sys.modules', {
        'ai': mock_ai,
        'ai.q_learning': mock_q_learning,
        'ai.q_learning.q_agent': mock_q_agent,
        'ai.mcts': mock_mcts,
        'ai.mcts.mcts_agent': mock_mcts_agent,
        'core': mock_core,
        'core.board': mock_board
    }):
        if 'web_api' in sys.modules:
            importlib.reload(sys.modules['web_api'])

        import web_api
        from web_api import bp


except Exception as e:
    print(f"=== DEBUG: Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()
    web_api = MagicMock()
    bp = MagicMock()


@pytest.fixture
def app():
    """Создание тестового Flask приложения"""
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def client(app):
    """Тестовый клиент Flask"""
    return app.test_client()


@pytest.fixture
def empty_board_3x3():
    return [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]


def test_health_endpoint(client):
    """Тест проверки работоспособности сервера"""
    print("\n=== Запуск test_health_endpoint ===")
    response = client.get('/ai/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'


def test_clear_cache_endpoint(client):
    """Тест очистки кеша"""
    print("\n=== Запуск test_clear_cache_endpoint ===")
    response = client.post('/ai/clear_cache')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'cache cleared'


def test_prepare_models_endpoint_success_fixed(client):
    """ИСПРАВЛЕННЫЙ тест успешной подготовки моделей"""
    print("\n=== Запуск test_prepare_models_endpoint_success_fixed ===")
    print(f"web_api module id: {id(web_api)}")
    print(f"prepare_models_for_web function: {web_api.prepare_models_for_web}")

    original_func = web_api.prepare_models_for_web

    try:
        web_api.prepare_models_for_web = MagicMock(return_value=True)

        print(f"Mock установлен: {web_api.prepare_models_for_web}")
        print(f"Mock return_value: {web_api.prepare_models_for_web.return_value}")

        response = client.post('/ai/prepare_models')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")

        data = json.loads(response.data)
        print(f"Parsed data: {data}")

        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['prepared'] is True, f"Expected True but got {data['prepared']}"

    finally:
        web_api.prepare_models_for_web = original_func


def test_prepare_models_with_direct_mock(client):
    """Тест с прямым подменой функции"""
    print("\n=== Запуск test_prepare_models_with_direct_mock ===")

    original_func = web_api.prepare_models_for_web

    mock_func = MagicMock()
    mock_func.return_value = True

    web_api.prepare_models_for_web = mock_func

    try:
        response = client.post('/ai/prepare_models')
        data = json.loads(response.data)

        print(f"Response: {data}")
        print(f"Mock called: {mock_func.called}")

        assert response.status_code == 200
        assert data['status'] == 'success'
        assert data['prepared'] is True

        mock_func.assert_called_once()

    finally:
        web_api.prepare_models_for_web = original_func


def test_ai_move_basic(client, empty_board_3x3):
    """Базовый тест для /ai/move"""
    print("\n=== Запуск test_ai_move_basic ===")

    if hasattr(web_api, '_cache'):
        web_api._cache.clear()

    with patch('web_api.os.path.exists', return_value=False):
        data = {
            'board': empty_board_3x3,
            'size': 3,
            'symbol': 'X'
        }
        response = client.post('/ai/move', json=data)
        assert response.status_code == 200
        result = json.loads(response.data)
        assert 'row' in result
        assert 'col' in result


def test_mcts_move_basic(client, empty_board_3x3):
    """Базовый тест для /ai/mcts_move"""
    print("\n=== Запуск test_mcts_move_basic ===")
    data = {
        'board': empty_board_3x3,
        'size': 3,
        'symbol': 'X'
    }
    response = client.post('/ai/mcts_move', json=data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'row' in data
    assert 'col' in data


# тут чисто тесты на то что pytest у меня работает - у меня долго в этом проекте почему то пайтест не работал
def test_simple_first():
    """Первый простой тест для проверки"""
    print("Тэсты запустились")
    assert 1 + 1 == 2


def test_math():
    """Простой математический тест"""
    assert 2 * 2 == 4


def test_string():
    """Простой строковый тест"""
    assert "hello".upper() == "HELLO"


def test_list():
    """Простой тест списка"""
    assert [1, 2, 3] == [1, 2, 3]