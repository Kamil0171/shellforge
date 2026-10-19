from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.admin_duty.dynamic_router import router as dynamic_admin_duty_router
from app.admin_duty.router import router as admin_duty_router
from app.config import APP_DESCRIPTION, APP_NAME, APP_VERSION
from app.database import create_db_and_tables
from app.routers import (
    about,
    dashboard,
    flashcards,
    health,
    home,
    lessons,
    quizzes,
    roadmap,
)
from app.seed import seed_database

templates = Jinja2Templates(directory="app/templates")


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


def is_html_navigation(request: Request) -> bool:
    path = request.url.path
    json_or_resource_paths = ("/api", "/admin-duty/dynamic/api", "/health", "/static")
    if any(path == prefix or path.startswith(prefix + "/") for prefix in json_or_resource_paths):
        return False
    if path in {"/openapi.json", "/docs", "/redoc"}:
        return False
    return request.method in {"GET", "HEAD"} or (
        request.method == "POST" and path.startswith("/quiz/")
    )


def html_error_response(request: Request, status_code: int, headers=None):
    return templates.TemplateResponse(
        request=request,
        name="404.html" if status_code == 404 else "error.html",
        context={"status_code": status_code},
        status_code=status_code,
        headers=headers,
    )


@app.exception_handler(RequestValidationError)
async def custom_validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    if is_html_navigation(request):
        return html_error_response(request, 422)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Nieprawidłowe dane żądania.",
        },
    )


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    if is_html_navigation(request):
        return html_error_response(request, exc.status_code, exc.headers)
    return await http_exception_handler(request, exc)


app.include_router(home.router)
app.include_router(lessons.router)
app.include_router(quizzes.router)
app.include_router(dashboard.router)
app.include_router(flashcards.router)
app.include_router(health.router)
app.include_router(roadmap.router)
app.include_router(about.router)
app.include_router(admin_duty_router)
app.include_router(dynamic_admin_duty_router)
