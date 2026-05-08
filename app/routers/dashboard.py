from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import LearningModule, Lesson, Quiz, QuizQuestion


router = APIRouter(prefix="/dashboard", tags=["dashboard"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard_page(request: Request, session: Session = Depends(get_session)):
    modules_count = len(session.exec(select(LearningModule)).all())
    lessons_count = len(session.exec(select(Lesson)).all())
    quizzes_count = len(session.exec(select(Quiz)).all())
    questions_count = len(session.exec(select(QuizQuestion)).all())

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "modules_count": modules_count,
            "lessons_count": lessons_count,
            "quizzes_count": quizzes_count,
            "questions_count": questions_count,
        },
    )