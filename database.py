from sqlmodel import SQLModel,create_engine, Field, Session,select,text
from datetime import date
from .enums import Priority,Status
from contextlib import asynccontextmanager
from fastapi import FastAPI,Depends
from typing import Annotated
from pydantic import EmailStr


connection_args={"check_same_thread":False}
engine=create_engine('sqlite:///./taskmanager.db',connect_args=connection_args)


class TaskIn(SQLModel):
    name: str
    description: str | None = None
    due_date: date
    priority: Priority
    status: Status
    assigned_to: str
    user_id: int = Field(default=None,foreign_key="usertable.id")

class TaskTable(TaskIn,table=True):
    id: int = Field(default=None,primary_key=True)

class UserLogin(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    password: str

class UserIn(UserLogin):
    name: str

class UserOut(SQLModel):
    id: int | None
    name: str
    email: EmailStr

    
class UserTable(UserIn,table=True):
    id: int = Field(default=None,primary_key=True)


async def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


#This is for creating database and tables during app startup
@asynccontextmanager
async def lifespan(app:FastAPI):
    await create_db_and_tables()
    yield

def get_session():
    with Session(engine) as session:
        session.exec(text("PRAGMA foreign_keys = ON")) #for each session we should explicitly enforce foreignkey for SQLite. In postgres its not required
        yield session

session_dependency = Annotated[Session,Depends(get_session)]




