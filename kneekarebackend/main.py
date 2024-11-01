from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from sqlmodel import SQLModel, create_engine, Field, Session, select
from typing import List, Optional
from datetime import datetime
from kneekarebackend.routers.users import user_router, User

DATABASE_URL = "sqlite:///instance/kneekare.db"
engine = create_engine(DATABASE_URL, echo=True)

    
class KneeData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    timestamp: datetime = Field(default_factory=datetime.now)
    angle: float
    rotation: float
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()
app.include_router(user_router)

# CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8080",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Use lifespans instead of on_event decorator
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.get("/health")
async def health():
    return {"status": "ok"}


# Start the server using Poetry scripts
def start():
    uvicorn.run("kneekarebackend.main:app", host="localhost", port=8000, reload=True)
