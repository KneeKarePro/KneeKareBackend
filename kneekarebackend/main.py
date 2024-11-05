from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from kneekarebackend.routers.users import user_router
from kneekarebackend.database import create_db_and_tables


# Create the FastAPI app
app = FastAPI(title="KneeKare Backend", description="Backend for KneeKare application")

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


# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}


# Start the server using Poetry scripts
def start():
    """
    Start the FastAPI server using the uvicorn server

    :return: None
    """
    uvicorn.run("kneekarebackend.main:app", host="localhost", port=8000, reload=True)
