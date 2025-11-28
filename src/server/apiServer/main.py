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
    allow_origins=["http://0.0.0.0:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware to print globals
@app.middleware("http")
async def print_globals_middleware(request, call_next):
    print("Globals information:")
    from globals import devices
    import json
    print(json.dumps(devices, indent=4, ensure_ascii=False))
    response = await call_next(request)
    return response

app.include_router(appRouter)
app.include_router(authRouter)
app.include_router(processRouter)
app.include_router(authClientRouter)