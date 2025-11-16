from pydantic import BaseModel

class DeviceAuth(BaseModel):
    device_id: int
    password: str
