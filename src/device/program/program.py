import threading
import time
import json
import requests
import os

class Program:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url

        self.device_id = None
        self.password = None
        self.session_id = None
        self.session_expiration = None # relevant id date
        
        self.command_queue = [] # commands

        self.running = False # stop threads command

        self.running_processes = []

        self.config_filename = "device_data.json" # file with settings
        self.load_config() # if this file is exists it load it

    # load data from json
    def load_config(self):
        if os.path.exists(self.config_filename):
            try:
                with open(self.config_filename, 'r') as f:
                    data = json.load(f)
                    self.device_id = data.get("device_id")
                    self.password = data.get("password")
                    self.session_id = data.get("session_id")
                    self.session_expiration = data.get("session_expiration")
            except Exception as e:
                print(f"Error loading data: {e}")

    # save data to json
    def save_config(self):
        data = {
            "device_id": self.device_id,
            "password": self.password,
            "session_id": self.session_id,
            "session_expiration": self.session_expiration
        }
        try:
            with open(self.config_filename, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {e}")

    #############################################

    # register device
    def register(self):
        try:
            url = f"{self.server_url}/device/auth/register"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.device_id = data["id"]
                self.password = data["password"]
                self.session_id = data["session_id"]
                self.session_expiration = time.time() + 3600  # Assume 1 hour expiration
                self.save_config()
                print(f"Registered: ID {self.device_id}, Password {self.password}")
            else:
                print(f"Registration failed: {response.status_code}")
        except Exception as e:
            print(f"Error during registration: {e}")

    # auth if session id is relevant
    def authorize(self):
        if self.session_expiration is None or time.time() > self.session_expiration:
            try:
                url = f"{self.server_url}/device/auth/startSession"
                payload = {"device_id": self.device_id, "password": self.password}
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    data = response.json()
                    self.session_id = data["session_id"]
                    self.session_expiration = time.time() + 3600  # Assume 1 hour expiration
                    self.save_config()
                    print(f"Re-authorized: new session_id {self.session_id}")
                else:
                    print(f"Authorization failed: {response.status_code}")
            except Exception as e:
                print(f"Error during authorization: {e}")

    #############################################

    # listen server for commands
    def listen_for_commands(self):
        while self.running:
            try:
                url = f"{self.server_url}/device/process/getCommands"
                headers = {"Authorization": self.session_id}
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    commands = response.json()
                    for command in commands:
                        self.command_queue.append(command)
                elif response.status_code == 403:
                    self.authorize()
                    print(403)
                else:
                    print(f"Failed to get commands: {response.status_code}")
            except Exception as e:
                print(f"Error listening for commands: {e}")

            print(self.command_queue)
            time.sleep(5)  # Poll every 5 seconds

    # start command
    def execute_command(self):
        while self.running:
            time.sleep(1)  # Small delay to avoid busy loop

    # send data to server
    def send_data(self, data):
        # TODO: POST data to some endpoint with Authorization
        pass

    # start threads for program
    def start_connection(self):
        self.running = True
        listener_thread = threading.Thread(target=self.listen_for_commands)
        executor_thread = threading.Thread(target=self.execute_command)
        listener_thread.start()
        executor_thread.start()

    # main function for start
    def start(self):
        if self.device_id is None:
            self.register()
        # else:
        self.authorize()
        self.start_connection()       

 
pr = Program()
pr.start()
