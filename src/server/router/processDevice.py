from fastapi import APIRouter, Request, Response, HTTPException, status
from fastapi.responses import StreamingResponse
import time
import uuid
import os
import hashlib
from models.device import DeviceAuth
from globals import *
from router.authClient import find_user_by_session_id
from router.authDevice import find_device_by_session_id, clean_device_command

processRouter = APIRouter(prefix="/device/process")

@processRouter.get("/getCommands")
def getCommands(request: Request):
    sessionID = request.headers.get("Authorization")

    device_id, device_data = find_device_by_session_id(sessionID)

    if device_id == None or device_data == None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden"
        )

    if (len(device_data["commands"])):
        copyData = device_data["commands"]
    else:
        copyData = []

    clean_device_command(device_id)
    return  copyData


@processRouter.get("/getCommandsClient")
def getCommandsClient(request: Request):
    sessionID = request.headers.get("Authorization")

    user_login, user_data = find_user_by_session_id(sessionID)

    if user_login is None:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    data = request.query_params
    device_id = data.get("device_id")

    if device_id not in devices:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    return devices[device_id]["commands"]


# adding command to device
@processRouter.post("/addCommand")
async def addCommand(request: Request):
    sessionID = request.headers.get("Authorization")

    user_login, user_data = find_user_by_session_id(sessionID)

    if user_login is None:
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    data = await request.json()
    device_id = data.get("device_id")
    command = data.get("command")

    if device_id not in devices:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )

    devices[device_id]["commands"].append(command)

    return {"status": "Command added successfully"}

