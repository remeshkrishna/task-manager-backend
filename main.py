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

def authenticate(username,password):
    print("executing")
    user =  [user for user in users if user.email==username]
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User doesn't exist")
    if not verify_password(user[0].password,password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Credentials")


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

@app.get('/items')
def get_items(token: Annotated[str,Depends(oauth2_scheme)]):
    pass

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

# @app.post("/signin",
#           response_model=Union[UserOutput , dict],
#           tags=["users"],
#           status_code=200,
#           responses={
#               401: {
#                   "description": "Unauthorized",
#                   "content":{
#                       "application/json":{
#                           "example":{"detail":"Invalid credentials"}
#                       }
#                   }
#               },
#               404: {
#                   "description":"User not found",
#                   "content":{
#                       "application/json":{
#                           "example": {"detail":"User not exist"}
#                       }
#                   }
#               }
#           }) #we can use either Union or | We selected Union because it is backward compatible..and | is introduced in python 3.10 
# def signin(user: LoginInput):
#     user_found = [i for i in users if i.email==user.email]
#     print(user_found)
#     if user_found:
#         if user.password == user_found[0].password:
#             return user_found[0]
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid credentials"
#                 )
#     else:
#         raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="User not exist"
#                 )

@app.get('/users' ,response_model=list[UserOutput],status_code=200, tags=["users"])
def get_all_users():
    return users

@app.get('/tasks' ,response_model=list[Task],status_code=200,tags=["tasks"])
def get_tasks():
    return tasks

@app.post('/tasks',status_code=201,tags=["tasks"])
def add_task(task: Task):
    tasks.append(task)
    return task
