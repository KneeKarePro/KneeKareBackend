from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime


class KneeData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.now)
    angle: float
    rotation: float
