from fastapi import FastAPI
from router.app import mainRouter

app = FastAPI()
app.include_router(mainRouter) 

value = {"hello"}

app.state.shared_config = {
    "devices":[]
}

