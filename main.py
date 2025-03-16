from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from enum import Enum
from fastapi.middleware.cors import CORSMiddleware
from datetime import date,timedelta,datetime,timezone
from typing import Union, Annotated
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext

# openssl rand -hex 32
SECRET_KEY = "786135a96e8ef75f56400da507a42abfb6749e5a31593d35c659fd597c518bee"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_methods = ['*'],
    allow_headers= ['*']
    
    )
tasks = {}
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
    id: int | None = 0
    name: str
    description: str | None = None
    due_date: date
    priority: Priority
    status: Status
    assigned_to: str

def authenticate(username,password):
    print("executing")
    user =  [user for user in users if user.email==username]
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User doesn't exist")
    if not verify_password(user[0].password,password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials", headers={"WWW-Authenticate":"Bearer"})


def create_hashed_password(password):
    return pwd_context.hash(password)

def verify_password(hashed_password, plain_password):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data: dict):
    updated_data = data.copy()
    expire_time = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    updated_data.update({"exp":expire_time})
    encoded_data = jwt.encode(payload=updated_data,key=SECRET_KEY,algorithm=ALGORITHM)
    return encoded_data

def decode_access_token(token: Annotated[str,Depends(oauth2_scheme)]):
    token_obj = jwt.decode(token,key=SECRET_KEY,algorithms=[ALGORITHM])
    print(token_obj)
    username=token_obj["sub"]
    return username

def get_current_user(username: Annotated[str,Depends(decode_access_token)]):
    user_found = [u for u in users if u.email==username]
    if not user_found:
        raise HTTPException(status_code=404,detail="Invalid user")
    return user_found


@app.get('/',include_in_schema=False)#This will be excluded from documentation
def home():
    return {"message":"success"}

@app.post("/signup",
          response_model=Union[UserOutput , dict],
          tags=["users"],
          status_code=201,
          responses={
              409: {
                  "content":{
                      "application/json":{
                          "example": {"detail": "User already exist"}
                      }
                  }
              }
          }
          )
def signup(user: SignupInput):
    user_found = [i for i in users if i.email==user.email]
    if user_found:
        raise HTTPException(
             status_code=status.HTTP_409_CONFLICT,
             detail={"message":"Email already exist"})
    new_user = User(id=len(users)+1,email = user.email, password=create_hashed_password(user.password),name= user.name)
    users.append(new_user)
    return new_user

@app.post('/token',
          responses={
              200:{
                  "content":{
                      "application/json":{
                          "example":{"access_token":"string", "token_type":"bearer"}
                      }
                  }
              },
              401: {
                  "description": "Unauthorized",
                  "content":{
                      "application/json":{
                          "example":{"detail":"Invalid credentials"}
                      }
                  }
              },
              404: {
                  "description":"User not found",
                  "content":{
                      "application/json":{
                          "example": {"detail":"User not exist"}
                      }
                  }
              }
          })
def get_access_token(formData: Annotated[OAuth2PasswordRequestForm,Depends()]):
    authenticate(formData.username,formData.password)
    access_token = create_access_token({"sub":formData.username})
    return {"access_token":access_token, "token_type":"bearer"}

@app.get('/users' ,response_model=list[UserOutput],status_code=200, tags=["users"])
def get_all_users():
    return users

@app.get('/tasks' ,response_model=list[Task],status_code=200,tags=["tasks"])
def get_tasks(user: Annotated[User,Depends(get_current_user)] ):
    return tasks[user.email]

@app.post('/tasks',status_code=201,tags=["tasks"])
def add_task(task: Task, user: Annotated[list[User],Depends(get_current_user)]):
    task.id = len(tasks)+1
    if user[0].email in tasks:
        tasks[user[0].email].append(task)
    else:
        tasks[user[0].email] = [task]
    return task
