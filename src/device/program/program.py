import threading
import time
import json
import requests
import os
from modules.door import Door

class Program:
    program_list = {
        1: Door
    }

    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url

        # auth settings
        self.device_id = None
        self.password = None
        self.session_id = None
        self.session_expiration = None # relevant id date

        self.config_filename = "device_data.json" # file with settings
        self.load_config() # if this file is exists it load it

        #program data
        self.running = False # stop threads command

        # data for thread works
        self.running_processes = []
        self.command_queue = [] # commands

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

    def find_process_by_id(self, id):
        for process in self.running_processes:
            if process.id == id:
                return process

    def max_process_id(self):
        maxId = 0
        for process in self.running_processes:
            if maxId < process.id:
                maxId = process.id
        return maxId

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
        print("start")
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
        print("start listening")
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

            print(f"commands: {self.command_queue}")
            
            # TODO: delete
            temp = input("")
            if temp:
                self.running = False 
            # time.sleep(5)  # Poll every 5 seconds

    def stop_all_processes(self):
        print("stopping all processes")
        for process in self.running_processes:
            process.stop()

    # start command
    def execute_command(self):
        while self.running:
            if self.command_queue:
                command = self.command_queue.pop(0)
                print("start executing command:")
                print(command)
            
                # Start command
                if command["type"] == "start":
                    print("start command")
                    try:
                        if command["programId"] in self.program_list.keys():
                            process_thread = self.program_list[command["programId"]](self.max_process_id()+1, command["programId"])
                            process_thread.start()
                            self.running_processes.append(process_thread)
                    except Exception as e:
                        print(f"error:{e}")

                # Stop command
                elif command["type"] == "stop":
                    print("stop command")
                    try:
                        self.find_process_by_id(command["processId"]).stop()
                    except Exception as ex:
                        print(f"not found: {ex}")
                
                # TODO: add DELETE PROGRAM
            time.sleep(1)  # Small delay to avoid busy loop
        self.stop_all_processes()


    # send data to server
    def send_data(self):
        print("start sending data")
        while self.running:
            if self.running_processes:
                for process in self.running_processes:        
                    print(f"sending data about process {process.id}")
                    url = f"{self.server_url}/device/process/addProcessInfo"
                    headers = {"Authorization": self.session_id}
                    data = [{
                            "process_id": process.id,
                            "status": process.status,
                            "output": process.output,
                            "programId": process.programId,
                        }
                    ]
                    try:
                        response = requests.post(url, json=data, headers=headers)
                        if response.status_code != 200:
                            print(f"Failed to send data for process {process.id}: {response.status_code}")
                    except Exception as e:
                        print(f"Exception sending data for process {process.id}: {e}")
            time.sleep(5)  # Small delay to avoid busy loop

    #############################################

    # start threads for program
    def start_connection(self):
        self.running = True
        listener_thread = threading.Thread(target=self.listen_for_commands)
        executor_thread = threading.Thread(target=self.execute_command)
        send_data_thread = threading.Thread(target=self.send_data)
        listener_thread.start()
        executor_thread.start()
        send_data_thread.start()

    # main function for start
    def start(self):
        if self.device_id is None:
            self.register()
        else:
            self.authorize()
        self.start_connection()


pr = Program("http://127.0.0.1:8000")
pr.start()
