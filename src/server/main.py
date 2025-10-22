from fastapi import FastAPI
from router.appDevice import appRouter
from router.authDevice import authRouter
from router.processDevice import processRouter
from router.authClient import authClientRouter

app = FastAPI()
app.include_router(appRouter) 
app.include_router(authRouter) 
app.include_router(processRouter) 
app.include_router(authClientRouter) 