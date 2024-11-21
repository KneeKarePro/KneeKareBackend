# Package Imports
from fastapi import APIRouter
from sqlmodel import Session, select, SQLModel, Field
from typing import List, Optional
from datetime import datetime
import pandas as pd

# Local Imports
from kneekarebackend.models.user import User  # Import the User
from kneekarebackend.models.kneedata import KneeData  # Import the KneeData
from kneekarebackend.database import engine  # Import the database engine


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


@user_router.get("/{user_id}", response_model=User)
async def read_user(user_id: int):
    """
    Get a user by their id

    - Args
        user_id (int): The id of the user to be retrieved

    - Returns
        User: The user with the specified id
    """
    with Session(engine) as session:
        user = session.get(User, user_id)
        return user


# Get all user knee data
@user_router.get("/{user_id}/knee-data", response_model=List[KneeData])
async def read_user_knee_data(user_id: int):
    """
    Get all knee data for a user

    - Args
        user_id (int): The id of the user to get knee data for

    - Returns
        List[KneeData]: A list of all knee data for the user
    """
    with Session(engine) as session:
        user = session.get(User, user_id)
        knee_data = session.exec(
            select(KneeData).filter(KneeData.user_id == user_id)
        ).all()
        return knee_data


# Create knee data for a user
@user_router.post("/{user_id}/knee-data", response_model=KneeData)
async def create_user_knee_data(user_id: int, knee_data: KneeData):
    """
    Create knee data for a user with pandas timestamp handling

    - Args
        user_id (int): The id of the user to create knee data for
        knee_data (KneeData): The knee data to be created

    - Returns
        KneeData: The knee data that was created
    """
    with Session(engine) as session:
        # Convert timestamp to datetime if it's a pandas Timestamp
        
        knee_data.timestamp = datetime.fromtimestamp(knee_data.timestamp)
        knee_data.user_id = user_id
        session.add(knee_data)
        session.commit()
        session.refresh(knee_data)
        return knee_data
