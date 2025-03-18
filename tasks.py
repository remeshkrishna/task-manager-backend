from fastapi import APIRouter,Depends,HTTPException,status
from .database import TaskTable as Task,TaskIn,UserTable as User,session_dependency
from typing import Annotated
from .authentication import get_current_user
from sqlmodel import select,Session

router=APIRouter(tags=['tasks'])

def fetch_all_tasks(session: Session):
    query=select(Task)
    tasks=session.exec(query).all()
    return tasks

@router.get('/tasks' ,response_model=list[Task],status_code=200,tags=["tasks"])
def get_all_tasks(user: Annotated[User,Depends(get_current_user)],session: session_dependency ):
    tasks = fetch_all_tasks(session)
    return tasks

@router.post('/tasks',tags=["tasks"], response_model=Task)
def add_task(task:TaskIn, session: session_dependency):
    new_task = Task(**task.model_dump())
    session.add(new_task)
    session.commit()
    session.refresh(new_task)
    return  new_task

@router.get('/tasks/{task_id}',response_model=Task)
def get_task(task_id: int, session: session_dependency):
    query = select(Task).where(Task.id==task_id)
    task = session.exec(query).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task Not Found"
        )
    return task