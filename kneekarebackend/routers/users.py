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
    Create knee data for a user, preventing duplicates based on timestamp
    """
    with Session(engine) as session:
        # Convert timestamp to datetime
        timestamp = datetime.fromtimestamp(knee_data.timestamp)
        
        # Check for existing entry
        existing_data = session.exec(
            select(KneeData)
            .where(KneeData.user_id == user_id)
            .where(KneeData.timestamp == timestamp)
        ).first()
        
        if existing_data:
            return existing_data
            
        # Create new entry if none exists
        knee_data.timestamp = timestamp
        knee_data.user_id = user_id
        session.add(knee_data)
        session.commit()
        session.refresh(knee_data)
        return knee_data


@user_router.post("/{user_id}/knee-data/batch", response_model=List[KneeData])
async def create_user_knee_data_batch(user_id: int, knee_data_batch: List[KneeData]):
    """
    Create multiple knee data entries for a user in batch, preventing duplicates
    """
    with Session(engine) as session:
        results = []
        
        # Process in chunks for memory efficiency
        chunk_size = 1000
        for i in range(0, len(knee_data_batch), chunk_size):
            chunk = knee_data_batch[i:i + chunk_size]
            
            # Convert timestamps to datetime for the chunk
            timestamps = [datetime.fromtimestamp(data.timestamp) for data in chunk]
            
            # Check existing entries in bulk
            existing_data = session.exec(
                select(KneeData)
                .where(KneeData.user_id == user_id)
                .where(KneeData.timestamp.in_(timestamps))
            ).all()
            
            # Create dictionary of existing timestamps
            existing_timestamps = {data.timestamp: data for data in existing_data}
            
            # Process new entries
            new_entries = []
            for data in chunk:
                timestamp = datetime.fromtimestamp(data.timestamp)
                if timestamp not in existing_timestamps:
                    data.timestamp = timestamp
                    data.user_id = user_id
                    new_entries.append(data)
                    results.append(data)
                else:
                    results.append(existing_timestamps[timestamp])
            
            # Bulk insert new entries
            if new_entries:
                session.add_all(new_entries)
                session.commit()
        
        return results
