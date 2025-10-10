# download file from server and add it to autostart
import winreg as reg
import os

class Autostart: 
    _path_file = "" # path to download file
    _key_name = "" # reg name

    def __init__(self, path_file: str, key_name: str):
        self._path_file = path_file
        self._key_name = key_name

    def install(self) -> int:

        try:
            registry_key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(registry_key, self._key_name, 0, reg.REG_SZ, self._path_file)            
            reg.CloseKey(registry_key)
        except:
            return 1
        return 0


# TODO: добавить файлы для запуска
program = Autostart(r"C:\Users\koji\Desktop\littleBitch\src\scripts\test.bat", "testPython")
program.install()