from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import os
from globals import config

appRouter = APIRouter(prefix="/app")


# download the main file
@appRouter.get("/download")
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

@appRouter.get("/version")
def print_version():
    return {"version": config["version"]}