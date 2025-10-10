
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import os

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