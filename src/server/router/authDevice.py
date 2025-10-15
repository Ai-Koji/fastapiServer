from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
import time
import uuid
import os
import hashlib
from models.device import DeviceAuth
from globals import *
import random
import string

authRouter = APIRouter(prefix="/device/auth")

# TODO: add clean sessoinId from DB by time

def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

# Contain list of registered devices
@authRouter.get("/register")
def register(request: Request):
    # generate userID, password
    if len(devices.keys()) > 0:
        device_id = max(devices.keys()) +1
    else:
        device_id = 1

    password = generate_password()

    # generate sessionID
    session_uuid = uuid.uuid4()
    timestamp = int(time.time())
    if device_id:
        base_string = f"{device_id}{session_uuid}{timestamp}"
        session_id = hashlib.sha256(base_string.encode()).hexdigest()[:32]
    else:
        session_id = str(session_uuid)

    # save info to db and json
    devices[device_id] = {
        "account": {
            "id": device_id, 
            "password": password, 
        },
        "sessionID": session_id,
        "sessionIDDate": time.time()
        }

    # TODO: save to db

    return {"id": device_id, "password": password, "session_id": session_id}


@authRouter.post("/startSession")
async def login(device: DeviceAuth):
    # check data:
    if not device.device_id in list(devices.keys()) or devices[device.device_id]["account"]["password"] != device.password:
        return Response(status_code=403)

    # generate sessionID
    session_uuid = uuid.uuid4()
    timestamp = int(time.time())
    if device.device_id:
        base_string = f"{device.device_id}{session_uuid}{timestamp}"
        session_id = hashlib.sha256(base_string.encode()).hexdigest()[:32]
    else:
        session_id = str(session_uuid)
        
    devices[device.device_id]["sessionID"] = session_id
    devices[device.device_id]["sessionIDDate"] = time.time()

    return {"session_id": session_id}