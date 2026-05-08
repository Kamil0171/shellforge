import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import LearningModule, Lesson, Quiz


router = APIRouter(prefix="/lessons", tags=["lessons"])

templates = Jinja2Templates(directory="app/templates")


def lesson_to_dict(lesson: Lesson, module: LearningModule, quiz: Quiz | None = None):
    return {
        "id": lesson.id,
        "title": lesson.title,
        "module": module.title,
        "level": lesson.level,
        "duration": lesson.duration,
        "description": lesson.description,
        "theory": lesson.theory,
        "commands": json.loads(lesson.commands_json),
        "practice_task": lesson.practice_task,
        "common_mistakes": json.loads(lesson.common_mistakes_json),
        "summary": lesson.summary,
        "quiz_id": quiz.id if quiz else None,
    }


@router.get("/")
def lessons_page(request: Request, session: Session = Depends(get_session)):
    lessons = session.exec(select(Lesson)).all()

    lessons_data = []

    for lesson in lessons:
        module = session.get(LearningModule, lesson.module_id)

        if module is None:
            continue

        quiz = session.exec(
            select(Quiz).where(Quiz.lesson_id == lesson.id)
        ).first()

        lessons_data.append(lesson_to_dict(lesson, module, quiz))

    return templates.TemplateResponse(
        request=request,
        name="lessons.html",
        context={
            "lessons": lessons_data,
        },
    )


@router.get("/{lesson_id}")
def lesson_detail_page(
    request: Request,
    lesson_id: int,
    session: Session = Depends(get_session),
):
    lesson = session.get(Lesson, lesson_id)

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lekcja nie została znaleziona.",
        )

    module = session.get(LearningModule, lesson.module_id)

    if module is None:
        raise HTTPException(
            status_code=404,
            detail="Moduł lekcji nie został znaleziony.",
        )

    quiz = session.exec(
        select(Quiz).where(Quiz.lesson_id == lesson.id)
    ).first()

    return templates.TemplateResponse(
        request=request,
        name="lesson_detail.html",
        context={
            "lesson": lesson_to_dict(lesson, module, quiz),
        },
    )