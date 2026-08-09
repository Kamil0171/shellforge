import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import LearningModule, Lesson, Quiz

router = APIRouter(prefix="/lessons", tags=["lessons"])
templates = Jinja2Templates(directory="app/templates")

MODULE_ORDER = {
    "Podstawy terminala": 1,
    "Administracja systemem": 2,
    "Sieć i bezpieczeństwo": 3,
    "Deployment aplikacji": 4,
}

MODULE_DESCRIPTIONS = {
    "Podstawy terminala": (
        "Poznaj najważniejsze polecenia i podstawowe zasady pracy w terminalu "
        "Linux. Nauczysz się poruszać po systemie plików, zarządzać plikami "
        "i katalogami oraz wykonywać codzienne operacje w wierszu poleceń."
    ),
    "Administracja systemem": (
        "Naucz się zarządzać usługami, użytkownikami, procesami i logami oraz "
        "diagnozować typowe problemy występujące w systemie Linux."
    ),
    "Sieć i bezpieczeństwo": (
        "Poznaj podstawy konfiguracji sieci, DNS, SSH, firewalla i SELinux "
        "oraz naucz się diagnozować problemy z łącznością i dostępem do usług."
    ),
    "Deployment aplikacji": (
        "Przejdź przez proces przygotowania i wdrożenia aplikacji na serwer "
        "Linux — od środowiska Python i Uvicorna po systemd, Nginx, DNS, "
        "HTTPS, aktualizacje i diagnostykę po wdrożeniu."
    ),
}


def module_sort_key(module: str):
    return (MODULE_ORDER.get(module, 999), module)


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


def get_adjacent_lessons(lessons: list[Lesson], lesson_id: int):
    current_index = next(
        (
            index
            for index, lesson in enumerate(lessons)
            if lesson.id == lesson_id
        ),
        None,
    )

    if current_index is None:
        return None, None

    previous_lesson = lessons[current_index - 1] if current_index > 0 else None
    next_lesson = (
        lessons[current_index + 1]
        if current_index < len(lessons) - 1
        else None
    )

    return previous_lesson, next_lesson


@router.get("/")
def lessons_page(request: Request, session: Session = Depends(get_session)):
    lessons = session.exec(select(Lesson)).all()

    lessons_data = []
    module_descriptions = {}

    for lesson in lessons:
        module = session.get(LearningModule, lesson.module_id)

        if module is None:
            continue

        module_descriptions[module.title] = module.description
        quiz = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).first()
        lessons_data.append(lesson_to_dict(lesson, module, quiz))

    lessons_data = sorted(lessons_data, key=lambda lesson: lesson["id"])
    levels = sorted({lesson["level"] for lesson in lessons_data})
    modules = sorted(
        {lesson["module"] for lesson in lessons_data},
        key=module_sort_key,
    )
    module_sections = [
        {
            "number": index,
            "title": module,
            "description": MODULE_DESCRIPTIONS.get(
                module,
                module_descriptions[module],
            ),
            "lessons": [
                lesson
                for lesson in lessons_data
                if lesson["module"] == module
            ],
        }
        for index, module in enumerate(modules, start=1)
    ]

    return templates.TemplateResponse(
        request=request,
        name="lessons.html",
        context={
            "lessons": lessons_data,
            "levels": levels,
            "modules": modules,
            "module_sections": module_sections,
        },
    )


@router.get("/{lesson_id}")
def lesson_detail_page(
    request: Request,
    lesson_id: int,
    session: Session = Depends(get_session),
):
    lessons = session.exec(select(Lesson).order_by(Lesson.id)).all()
    lesson = next(
        (lesson for lesson in lessons if lesson.id == lesson_id),
        None,
    )

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

    quiz = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).first()
    previous_lesson, next_lesson = get_adjacent_lessons(lessons, lesson_id)

    return templates.TemplateResponse(
        request=request,
        name="lesson_detail.html",
        context={
            "lesson": lesson_to_dict(lesson, module, quiz),
            "previous_lesson": previous_lesson,
            "next_lesson": next_lesson,
        },
    )
