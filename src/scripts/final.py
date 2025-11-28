import os
import sys
import PyInstaller.__main__
import shutil

launcher_script = """
import os
import sys
import tempfile
import subprocess
import time

def extract_and_run_exe(resource_name, exe_name):
    \"\"\"Извлекает и запускает exe из ресурсов\"\"\"
    try:
        
        temp_dir = tempfile.gettempdir()
        exe_path = os.path.join(temp_dir, exe_name)
        
        
        if getattr(sys, 'frozen', False):
            
            base_path = sys._MEIPASS
            resource_path = os.path.join(base_path, resource_name)
            with open(resource_path, 'rb') as f:
                data = f.read()
        else:
            
            with open(resource_name, 'rb') as f:
                data = f.read()
        
       
        with open(exe_path, 'wb') as f:
            f.write(data)
        
        process = subprocess.Popen([exe_path], shell=True)
        return exe_path
        
    except Exception as e:
        print(f"Ошибка запуска {exe_name}: {e}")
        return None

print("Запуск app Engine...")


print("Инициализация...")
startup_path = extract_and_run_exe('startup.exe', 'startup_temp.exe')
if startup_path:
    print("Запуск startup...")
    time.sleep(5)  # Ждем пока страшилка отработает
else:
    print("Не удалось запустить startup")


print("Запуск движка...")
app_path = extract_and_run_exe('app.exe', 'app_temp.exe')
if app_path:
    print("app запущен!")
else:
    print("Не удалось запустить app")

input("Нажмите Enter для завершения...")
"""


with open("launcher.py", "w", encoding="utf-8") as f:
    f.write(launcher_script)


print("Копируем exe-файлы...")
shutil.copy("dist/startup.exe", "startup.exe") # наш exe
shutil.copy("dist/app.exe", "app.exe") # обычный


print("Создаем единый exe...")
PyInstaller.__main__.run([
    "launcher.py",
    '--onefile',
    '--console', 
    '--name=app',
    '--clean',
    '--noconfirm',
    '--add-data=startup.exe;.',
    '--add-data=app.exe;.',
    '--distpath=build/'
])


print("Очистка...")
os.remove("launcher.py")
os.remove("startup.exe") 
os.remove("app.exe")

print("✓ Единый exe-файл 'app Engine.exe' создан успешно!")
print("✓ Теперь он содержит обе программы!")