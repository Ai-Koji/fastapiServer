from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import time
import uuid
import os
import hashlib
from models.device import DeviceAuth
from globals import *


processRouter = APIRouter(prefix="/device/process")

def find_by_session_id(session_id):
    for device_id, device_data in devices.items():
        if device_data["sessionID"] == session_id:
            return device_id, device_data
    return None, None

@processRouter.get("/getCommands")
def getCommands(request: Request):
    sessionID = request.headers.get("Authorization")

    device_id, device_data = find_by_session_id(sessionID)

    if device_id == None:
        return HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    return  device_data["commands"]

