from enum import Enum

class Command(Enum):
    LISTEN = 1

class Device:
    deviceCommand = Command.LISTEN
    def __init__(self, id:int, ip:str):
        self._id = id
        self.ip = ip

    def set_command(self, command:Command):
        self.deviceCommand = command
    def get_command(self):
        return self.deviceCommand
