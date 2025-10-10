from fastapi import FastAPI
from router.app import mainRouter

app = FastAPI()
app.include_router(mainRouter) 
    
@app.get("/")
def read_root():
    return {"message": "Главная страница API"}