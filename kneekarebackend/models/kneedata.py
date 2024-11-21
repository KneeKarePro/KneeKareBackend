from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from pydantic import field_validator
import pandas as pd


class KneeData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.now)
    angle: float
    rotation: float

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        if isinstance(value, str):
            if value.endswith('Z'):
                value = value[:-1]
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                if '.' in value:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return datetime.now()
