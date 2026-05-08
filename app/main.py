from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.database import create_db_and_tables
from app.routers import dashboard, flashcards, home, lessons, quizzes
from app.seed import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_database()
    yield


app = FastAPI(
    title="ShellForge",
    description="Edukacyjna aplikacja webowa do nauki Linuxa i DevOps.",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router)
app.include_router(lessons.router)
app.include_router(quizzes.router)
app.include_router(dashboard.router)
app.include_router(flashcards.router)