import subprocess
import sys
import os


def check_coverage():
    """Проверка покрытия тестами"""

    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(project_root, "backend")
    ai_path = os.path.join(project_root, "ai")

    os.environ['PYTHONPATH'] = f"{project_root}:{backend_path}:{ai_path}:{os.environ.get('PYTHONPATH', '')}"

    print("Проверка покрытия тестами...")
    print("=" * 50)

    print("\n1. Общее покрытие проекта:")
    cmd = ["pytest", "--cov=backend", "--cov=ai", "--cov=core", "--cov-report=term", "tests/"]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        for line in result.stdout.split('\n'):
            if any(keyword in line for keyword in ['TOTAL', 'backend', 'ai', 'core']) and '%' in line:
                print(f"   {line.strip()}")
        if result.stderr:
            print("\nОшибки во время проверки покрытия:")
            print(result.stderr)

    except Exception as e:
        print(f"Ошибка при выполнении проверки покрытия: {e}")
        return False

    return True


if __name__ == "__main__":
    success = check_coverage()
    sys.exit(0 if success else 1)