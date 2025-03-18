from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .users import router as user_router
from .authentication import router as auth_router
from .tasks import router as task_router
from .database import lifespan



app = FastAPI(
    lifespan=lifespan)

app.include_router(user_router)
app.include_router(task_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods = ['*'],
    allow_headers= ['*']
    )

@app.get('/',include_in_schema=False)#This will be excluded from documentation
def home():
    return {"message":"success"}







