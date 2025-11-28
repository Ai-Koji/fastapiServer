import os
import sys
import PyInstaller.__main__

# Получаем абсолютный путь к start.py (они в одной папке src)
current_dir = os.path.dirname(os.path.abspath(__file__))
start_script = os.path.join(current_dir, "script", "start.py")

print(f"Ищу файл: {start_script}")

# Проверяем существует ли файл
if not os.path.exists(start_script):
    print("ОШИБКА: Файл start.py не найден!")
    print("Проверь структуру папок:")
    print("littleBitch/")
    print("└── src/")
    print("    ├── script/")
    print("    │   └── start.py")
    print("    └── main.py")
    sys.exit(1)

print("Файл найден! Создаю exe...")

# Создаем exe-файл
PyInstaller.__main__.run([
    start_script,
    '--onefile',
    '--noconsole',
    '--name=startup',
    '--clean',
    '--uac-admin',
    '--noconfirm'
])