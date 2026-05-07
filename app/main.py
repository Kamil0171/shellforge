from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import home, lessons


app = FastAPI(
    title="ShellForge",
    description="Edukacyjna aplikacja webowa do nauki Linuxa i DevOps.",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(home.router)
app.include_router(lessons.router)