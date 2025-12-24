#!/usr/bin/env python3
"""
Простой скрипт для проверки покрытия тестами
"""

import subprocess
import sys
import os


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = f"{project_root}:{project_root}/backend:{os.environ.get('PYTHONPATH', '')}"

    print("📊 Проверка покрытия тестами")
    print("=" * 50)

    commands = [
        ["pytest", "--cov=backend", "backend/", "--cov-report=term"],
        ["pytest", "--cov=backend.web_api", "backend/test_api.py", "--cov-report=term-missing"],
        ["pytest", "--cov=backend.main", "backend/test_main.py", "--cov-report=term-missing"],
    ]

    for i, cmd in enumerate(commands, 1):
        print(f"\n🔍 Тест {i}: {' '.join(cmd)}")
        print("-" * 40)

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.stdout:
            for line in result.stdout.split('\n'):
                if 'TOTAL' in line or 'backend' in line or 'Coverage' in line:
                    print(line.strip())

        if result.stderr:
            print(f"Ошибки: {result.stderr[:200]}...")


if __name__ == "__main__":
    main()