from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import Flashcard, Lesson


router = APIRouter(prefix="/flashcards", tags=["flashcards"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/{lesson_id}")
def flashcards_page(
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

    flashcards = session.exec(
        select(Flashcard)
        .where(Flashcard.lesson_id == lesson.id)
        .order_by(Flashcard.position)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="flashcards.html",
        context={
            "lesson": lesson,
            "flashcards": flashcards,
        },
    )