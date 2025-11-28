from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import os
from globals import config

appRouter = APIRouter(prefix="/device/app")


# download the main file
@appRouter.get("/download/mainScript")
def download_large_file():
    file_path = "uploads/program.exe"
    
    def file_iterator():
        with open(file_path, mode="rb") as file:
            while chunk := file.read(8192):  # Читаем блоками по 8KB
                yield chunk 

    return StreamingResponse(
        file_iterator(),
        media_type="exe",
        headers={"Content-Disposition": "attachment; filename=program.exe"}
    )

# download an autostart script
@appRouter.get("/download/autostart")
def download_autostart_script():
    file_path = "uploads/autostart.exe"
    
    def file_iterator():
        with open(file_path, mode="rb") as file:
            while chunk := file.read(8192):  # Читаем блоками по 8KB
                yield chunk 

    return StreamingResponse(
        file_iterator(),
        media_type="exe",
        headers={"Content-Disposition": "attachment; filename=autostart.exe"}
    )

@appRouter.get("/version")
def print_version():
    return {"version": config["version"]}
