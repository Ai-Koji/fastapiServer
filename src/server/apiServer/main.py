from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from router.appDevice import appRouter
from router.authDevice import authRouter
from router.processDevice import processRouter
from router.authClient import authClientRouter

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appRouter)
app.include_router(authRouter)
app.include_router(processRouter)
app.include_router(authClientRouter)
