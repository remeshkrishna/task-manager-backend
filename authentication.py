from fastapi import HTTPException,status,Depends,APIRouter
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from passlib.context import CryptContext
from datetime import timedelta,timezone,datetime
from typing import Annotated
import jwt
from .database import session_dependency,UserTable as User
from pydantic import EmailStr
from sqlmodel import select,Session

router=APIRouter()

# openssl rand -hex 32
SECRET_KEY = "786135a96e8ef75f56400da507a42abfb6749e5a31593d35c659fd597c518bee"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fetch_user(email_id: EmailStr,session: Session):
    query = select(User).where(User.email==email_id)
    user=session.exec(query).first()
    return user

def authenticate(username,password,session):
    print("executing")
    user =  fetch_user(username,session)#[user for user in users if user.email==username]
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User doesn't exist")
    if not verify_password(user.password,password):
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

def get_current_user(username: Annotated[EmailStr,Depends(decode_access_token)],session: session_dependency):
    user_found = fetch_user(username,session)
    if not user_found:
        raise HTTPException(status_code=404,detail="Invalid user")
    return user_found

@router.post('/token',
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
def get_access_token(formData: Annotated[OAuth2PasswordRequestForm,Depends()],session: session_dependency):
    authenticate(formData.username,formData.password,session)
    access_token = create_access_token({"sub":formData.username})
    return {"access_token":access_token, "token_type":"bearer"}