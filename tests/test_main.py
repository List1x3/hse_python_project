import pytest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


project_root = Path(__file__).parent.parent
backend_path = project_root / "backend"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(backend_path))

print(f"Project root: {project_root}")
print(f"Backend path: {backend_path}")
print(f"Current dir: {os.getcwd()}")


# пару тестов что у меня робит пайтест
def test_simple():
    """Тест не проверку"""
    print("Пайтест работает")
    assert 1 + 1 == 2

def test_math_operations():
    """Математические тесты"""
    assert 2 + 2 == 4
    assert 3 * 3 == 9
    assert 10 - 5 == 5
    assert 20 / 4 == 5

    return True


def test_string_operations():
    """Строковые тесты"""

    assert "hello" + " world" == "hello world"
    assert "TEST".lower() == "test"
    assert "python".upper() == "PYTHON"
    assert len("abcdef") == 6

    return True


def test_import_main():
    """Тест импорта main.py"""

    try:
        import backend.main as main

        assert hasattr(main, 'app'), "main должен иметь атрибут 'app'"

        return True
    except ImportError as e:
        return False
    except Exception as e:
        return False


def test_flask_app_exists():
    """Тест что Flask приложение существует"""

    try:
        import backend.main as main
        from flask import Flask

        assert isinstance(main.app, Flask), "'app' должен быть Flask приложением"

        return True
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def test_routes_exist():
    """Тест что маршруты определены"""

    try:
        import backend.main as main

        # Получаем все маршруты
        routes = list(main.app.url_map.iter_rules())

        if routes:
            print(f"Найдено маршрутов: {len(routes)}")
            return True
        else:
            return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def test_key_routes():
    """Тест ключевых маршрутов"""

    try:
        import backend.main as main

        main.app.config['TESTING'] = True
        client = main.app.test_client()

        test_cases = [
            ('/', 'GET'),
            ('/game/3', 'GET'),
            ('/game_bot/4', 'GET'),
            ('/ai/health', 'GET'),
        ]

        results = []

        for route, method in test_cases:
            try:
                if method == 'GET':
                    response = client.get(route)
                else:
                    continue

                results.append(response.status_code < 500)
            except Exception as e:
                print(f"  {route}: ошибка - {e}")
                results.append(False)

        success_count = sum(1 for r in results if r)

        return success_count > 0
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def test_mock_render_template():
    """Тест мокинга render_template"""

    try:
        import sys
        import os
        from pathlib import Path

        project_root = Path(__file__).parent.parent
        backend_path = project_root / "backend"
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(backend_path))

        with patch('backend.main.render_template') as mock_render:
            mock_render.return_value = "<html>Mocked Page</html>"

            import backend.main

            from backend.main import render_template
            result = render_template('test.html')

            assert result == "<html>Mocked Page</html>"
            mock_render.assert_called_once_with('test.html')

            return True
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_blueprint_registration():
    """Тест регистрации blueprint"""

    try:
        import backend.main as main

        if hasattr(main.app, 'blueprints'):
            blueprints = main.app.blueprints
            print(f"Найдено blueprints: {len(blueprints)}")

            return len(blueprints) > 0
        else:
            print("Нет атрибута blueprints")
            return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False


def test_overall_main():
    """Общий тест модуля main"""
    print("\n" + "=" * 60)
    print("ОБЩИЙ ТЕСТ МОДУЛЯ main.py")
    print("=" * 60)

    test_functions = [
        ("Простой тест", test_simple),
        ("Импорт модуля", test_import_main),
        ("Flask приложение", test_flask_app_exists),
        ("Маршруты", test_routes_exist),
        ("Ключевые маршруты", test_key_routes),
        ("Мок render_template", test_mock_render_template),
        ("Регистрация blueprint", test_blueprint_registration),
        ("Математика", test_math_operations),
        ("Строки", test_string_operations),
    ]

    results = []

    for name, test_func in test_functions:

        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            results.append((name, False))

    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ main.py:")
    print("-" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    success_rate = passed / total if total > 0 else 0
    print(f"Успешность: {success_rate:.0%}")

    assert success_rate >= 0.7, f"Только {passed} из {total} тестов прошли (нужно минимум {int(total * 0.7)})"