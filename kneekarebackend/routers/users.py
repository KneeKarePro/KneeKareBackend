from fastapi import APIRouter
from sqlmodel import Session, select, SQLModel, Field
from typing import List, Optional
from kneekarebackend.main import engine

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str
    email: str
   
@user_router.get("/", response_model=List[User])
async def read_users():
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users
      
@user_router.post("/", response_model=User)
async def create_user(user: User):
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user