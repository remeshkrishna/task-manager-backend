from fastapi import APIRouter,HTTPException,status,Depends
from typing import Union,Annotated
from .database import session_dependency,UserOut,UserIn,UserTable as User
from .authentication import fetch_user,create_hashed_password,get_current_user
from sqlmodel import select,Session

router=APIRouter(
    tags=['users']
)

def add_user(user: User,session: Session):
    session.add(user)
    session.commit()
    session.refresh(user)

def fetch_all_users(session: Session):
    query = select(User)
    users=session.exec(query).all()
    return users

@router.post("/signup",
          response_model=Union[UserOut , dict],
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
          })
def signup(user: UserIn, session: session_dependency):
    user_found = fetch_user(user.email,session)

    if user_found:
        print(user_found.email)
        raise HTTPException(
             status_code=status.HTTP_409_CONFLICT,
             detail={"message":"Email already exist"})
    new_user = User(**user.model_dump())
    new_user.password=create_hashed_password(user.password)
    add_user(new_user,session)
    return new_user


@router.get('/users' ,response_model=list[UserOut],status_code=200, tags=["users"])
def get_all_users(session: session_dependency): 
    users = fetch_all_users(session)
    return users

@router.get('/user/{user_id}')
def get_user(user_id: int,session: session_dependency):
    query = select(User).where(User.id==user_id)
    user=session.exec(query).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get('/users/me',response_model=UserOut)
def get_me(user: Annotated[UserOut,Depends(get_current_user)]):
    return user