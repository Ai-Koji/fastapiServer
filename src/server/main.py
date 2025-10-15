from fastapi import FastAPI
from router.appDevice import appRouter
from router.authDevice import authRouter

app = FastAPI()
app.include_router(appRouter) 
app.include_router(authRouter) 