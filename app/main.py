from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.database import create_db_and_tables
from app.routers import dashboard, flashcards, health, home, lessons, quizzes
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_database()
    yield


app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router)
app.include_router(lessons.router)
app.include_router(quizzes.router)
app.include_router(dashboard.router)
app.include_router(flashcards.router)
app.include_router(health.router)