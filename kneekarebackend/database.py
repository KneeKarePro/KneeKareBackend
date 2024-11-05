from sqlmodel import SQLModel, create_engine, Field
from typing import Optional

DATABASE_URL = "sqlite:///instance/kneekare.db"
engine = create_engine(DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
