# routers/data.py
from fastapi import APIRouter, HTTPException
from sqlmodel import Session, select
from typing import List, Dict
from datetime import datetime
import pandas as pd
from pydantic import BaseModel

from kneekarebackend.models.user import User
from kneekarebackend.models.kneedata import KneeData
from kneekarebackend.database import engine

data_router = APIRouter(
    prefix="/data",
    tags=["data"]
)

class DataStats(BaseModel):
    mean: float
    std: float
    min: float
    max: float

class UserStats(BaseModel):
    username: str
    stats: Dict[str, DataStats]

@data_router.post("", status_code=201)
async def receive_data(username: str, angle: float, rotation: float):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == username)).first()
        if not user:
            user = User(name=username, password="", email="")
            session.add(user)
            session.commit()
            session.refresh(user)

        knee_data = KneeData(
            angle=angle,
            rotation=rotation,
            user_id=user.id
        )
        session.add(knee_data)
        session.commit()
        return {"message": "Data received"}

@data_router.get("/{username}", response_model=List[KneeData])
async def get_data(username: str, limit: int = 100):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        data = session.exec(
            select(KneeData)
            .where(KneeData.user_id == user.id)
            .order_by(KneeData.timestamp.desc())
            .limit(limit)
        ).all()
        print(len(data))
        data = data[::-1]
        # only return the limit number of data points
        return data[:limit]

@data_router.get("/range/{username}")
async def get_data_range(
    username: str,
    start_time: datetime,
    end_time: datetime
):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        data = session.exec(
            select(KneeData)
            .where(KneeData.user_id == user.id)
            .where(KneeData.timestamp >= start_time)
            .where(KneeData.timestamp <= end_time)
        ).all()
        return data

@data_router.get("/stats/{username}", response_model=UserStats)
async def get_data_stats(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        data = session.exec(
            select(KneeData).where(KneeData.user_id == user.id)
        ).all()
        
        df = pd.DataFrame([{
            'angle': d.angle,
            'rotation': d.rotation,
            'timestamp': d.timestamp
        } for d in data])

        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for user")

        stats = {
            'angle': DataStats(
                mean=float(df['angle'].mean()),
                std=float(df['angle'].std()),
                min=float(df['angle'].min()),
                max=float(df['angle'].max())
            ),
            'rotation': DataStats(
                mean=float(df['rotation'].mean()),
                std=float(df['rotation'].std()),
                min=float(df['rotation'].min()),
                max=float(df['rotation'].max())
            )
        }
        
        return UserStats(username=username, stats=stats)

@data_router.delete("/{username}")
async def delete_data(username: str):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == username)).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        session.delete(user)
        session.commit()
        return {"message": "Data deleted"}