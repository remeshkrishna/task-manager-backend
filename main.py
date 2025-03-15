from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from datetime import date
from typing import Union

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods = ['*'],
    allow_headers= ['*']
    
    )
tasks = []
users = []

class User(BaseModel):
    id: int | None = None
    name: str
    email: EmailStr
    password: str

class LoginInput(BaseModel):
    email: EmailStr
    password: str

class SignupInput(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOutput(BaseModel):
    id: int
    name: str
    email: EmailStr


class Priority(str,Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class Status(str,Enum):
    in_progress = "In Progress"
    pending = "Pending"
    completed = "Completed"

class Task(BaseModel):
    name: str
    description: str | None = None
    due_date: date
    priority: Priority
    status: Status
    assigned_to: str

@app.get('/',include_in_schema=False)#This will be excluded from documentation
def home():
    return {"message":"success"}

@app.post("/signup",response_model=Union[UserOutput , dict],status_code=201)
def signup(user: SignupInput):
    print("entered function")
    user_found = [i for i in users if i.email==user.email]
    if user_found:
        return {"message":"Email already exist"}
    new_user = User(id=len(users)+1,email = user.email, password=user.password,name= user.name)
    users.append(new_user)
    return new_user

@app.post("/signin",response_model=Union[UserOutput , dict], status_code=200) #we can use either Union or | We selected Union because it is backward compatible..and | is introduced in python 3.10 
def signin(user: LoginInput):
    user_found = [i for i in users if i.email==user.email]
    print(user_found)
    if user_found:
        if user.password == user_found[0].password:
            print("found")
            return user_found[0]
        else:
            return {"message": "Authentication Failed"}
    else:
        return {"message":"Invalid User"}

@app.get('/users' ,response_model=list[UserOutput],status_code=200)
def get_all_users():
    return users

@app.get('/tasks' ,response_model=list[Task],status_code=200)
def get_tasks():
    return tasks

@app.post('/tasks',status_code=201)
def add_task(task: Task):
    tasks.append(task)
    return task
