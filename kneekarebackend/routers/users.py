# Package Imports
from fastapi import APIRouter
from sqlmodel import Session, select, SQLModel, Field
from typing import List, Optional

# Local Imports
from kneekarebackend.models.user import User # Import the User model
from kneekarebackend.database import engine # Import the database engine


user_router: APIRouter = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
   
@user_router.get("/", response_model=List[User])
async def read_users():
    """
    Get all users from the database

    - Args
        None

    - Returns
        List[User]: A list of all users in the database
    """
    with Session(engine) as session:
        users = session.exec(select(User)).all()
        return users
      
@user_router.post("/", response_model=User)
async def create_user(user: User):
    """
    Create a new user in the database

    - Args
        user (User): The user to be created

    - Returns
        User: The user that was created
    """
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
