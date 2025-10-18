from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
import time
import uuid
import os
import hashlib
from models.user import UserAuth
from globals import *

authClientRouter = APIRouter(prefix=" /client/auth")

# TODO: add clean sessoinId from DB by time
# TODO: add sha256

def find_user_by_session_id(session_id):
    for login, user_data  in _clients.items():
        if user_data["sessionID"] == session_id:
            return login, user_data
    return None, None

@authClientRouter.post("/login")
async def login(user:UserAuth):
    # check data:
    if not user.login in list(_clients.keys()) or _clients[user.login]["password"] != device.password:
        return Response(status_code=403)

    # generate sessionID
    session_uuid = uuid.uuid4()
    timestamp = int(time.time())
    if device.device_id:    
        base_string = f"{client.login}{session_uuid}{timestamp}"
        session_id = hashlib.sha256(base_string.encode()).hexdigest()[:32]
    else:
        session_id = str(session_uuid)

    _clients[user.login]["sessionID"] = session_id
    _clients[user.login]["sessionIDDate"] = time.time()

    return {"session_id": session_id}


async def check_auth(request: Request, call_next):
    sessionID = request.headers.get("Authorization")
   
    if find_user_by_session_id(sessionID):
        return response

    return HTTPException(
        status_code=403,
        detail="Forbidden"
    )
