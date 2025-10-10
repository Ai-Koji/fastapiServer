
from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

mainRouter = APIRouter(prefix="/app")

# download the main file
@mainRouter.get("/download")
async def download_file():
    file_path = f"router/uploads/file.ttxt"
    return FileResponse(file_path)


@mainRouter.get("/")
async def main():
    return str(os.listdir())