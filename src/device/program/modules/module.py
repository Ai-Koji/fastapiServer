from time import sleep
import threading
import io
import sys

# Abstract class for modules
class Module(threading.Thread):    
    def __init__(self, id, programId):
        super().__init__()
        self.id = id
        self.programId = programId
        self.status = "stopped"
        self.output = ""

    def run(self):
        self.print("start script")

        self.running = True
        self.status = "started"

        try:
            self.execute_script()
        except Exception as ex:
            self.print(ex)

        self.running = False
        self.status = "stopped"

        self.print("end_script")
        
    def execute_script(self):
        pass

    def print(self, out):
        self.output += out + "\n"

    def stop(self):
        self.status = "stopped"
        self.running = False