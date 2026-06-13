import json

from sqlmodel import Session, select

from app.content.admin_directories import ADMIN_DIRECTORIES
from app.content.basic_system_diagnostics import BASIC_SYSTEM_DIAGNOSTICS
from app.content.file_permissions import FILE_PERMISSIONS
from app.content.files_and_directories import FILES_AND_DIRECTORIES
from app.content.network_diagnostics import NETWORK_DIAGNOSTICS
from app.content.package_management import PACKAGE_MANAGEMENT
from app.content.processes import PROCESSES
from app.content.system_logs import SYSTEM_LOGS
from app.content.system_services import SYSTEM_SERVICES
from app.content.terminal_navigation import TERMINAL_NAVIGATION
from app.content.text_files import TEXT_FILES
from app.content.users_and_groups import USERS_AND_GROUPS
from app.database import engine
from app.models import Flashcard, LearningModule, Lesson, Quiz, QuizAnswer, QuizQuestion

LESSONS = [
    TERMINAL_NAVIGATION,
    FILES_AND_DIRECTORIES,
    FILE_PERMISSIONS,
    USERS_AND_GROUPS,
    PROCESSES,
    TEXT_FILES,
    PACKAGE_MANAGEMENT,
    SYSTEM_SERVICES,
    NETWORK_DIAGNOSTICS,
    SYSTEM_LOGS,
    ADMIN_DIRECTORIES,
    BASIC_SYSTEM_DIAGNOSTICS,
]


def sync_module(session, module_data):
    module = session.exec(
        select(LearningModule).where(LearningModule.title == module_data["title"])
    ).first()

    if not module:
        module = LearningModule(
            title=module_data["title"],
            description=module_data["description"],
        )
        session.add(module)
    else:
        module.description = module_data["description"]

    session.commit()
    session.refresh(module)

    return module


def sync_lesson(session, module, lesson_data):
    lesson = session.exec(
        select(Lesson).where(
            Lesson.module_id == module.id,
            Lesson.title == lesson_data["title"],
        )
    ).first()

    lesson_values = {
        "module_id": module.id,
        "title": lesson_data["title"],
        "level": lesson_data["level"],
        "duration": lesson_data["duration"],
        "description": lesson_data["description"],
        "theory": lesson_data["theory"],
        "commands_json": json.dumps(lesson_data["commands"], ensure_ascii=False),
        "practice_task": lesson_data["practice_task"],
        "common_mistakes_json": json.dumps(
            lesson_data["common_mistakes"],
            ensure_ascii=False,
        ),
        "summary": lesson_data["summary"],
    }

    if not lesson:
        lesson = Lesson(**lesson_values)
        session.add(lesson)
    else:
        for field, value in lesson_values.items():
            setattr(lesson, field, value)

    session.commit()
    session.refresh(lesson)

    return lesson


def delete_quiz_questions(session, quiz):
    questions = session.exec(
        select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
    ).all()

    for question in questions:
        answers = session.exec(
            select(QuizAnswer).where(QuizAnswer.question_id == question.id)
        ).all()

        for answer in answers:
            session.delete(answer)

        session.delete(question)

    session.commit()


def sync_quiz(session, lesson, quiz_data):
    quiz = session.exec(select(Quiz).where(Quiz.lesson_id == lesson.id)).first()

    if not quiz:
        quiz = Quiz(
            lesson_id=lesson.id,
            title=quiz_data["title"],
            description=quiz_data["description"],
        )
        session.add(quiz)
    else:
        quiz.title = quiz_data["title"]
        quiz.description = quiz_data["description"]

    session.commit()
    session.refresh(quiz)

    delete_quiz_questions(session, quiz)

    for index, question_data in enumerate(quiz_data["questions"], start=1):
        question = QuizQuestion(
            quiz_id=quiz.id,
            text=question_data["text"],
            position=index,
        )
        session.add(question)
        session.commit()
        session.refresh(question)

        for option_key, answer_text, is_correct in question_data["answers"]:
            answer = QuizAnswer(
                question_id=question.id,
                option_key=option_key,
                text=answer_text,
                is_correct=is_correct,
            )
            session.add(answer)

    session.commit()

    return quiz


def sync_flashcards(session, lesson, flashcards_data):
    existing_flashcards = session.exec(
        select(Flashcard).where(Flashcard.lesson_id == lesson.id)
    ).all()

    for flashcard in existing_flashcards:
        session.delete(flashcard)

    session.commit()

    for index, flashcard_data in enumerate(flashcards_data, start=1):
        flashcard = Flashcard(
            lesson_id=lesson.id,
            question=flashcard_data["question"],
            answer=flashcard_data["answer"],
            position=index,
        )
        session.add(flashcard)

    session.commit()


def seed_database():
    with Session(engine) as session:
        for lesson_bundle in LESSONS:
            module = sync_module(session, lesson_bundle["module"])
            lesson = sync_lesson(session, module, lesson_bundle["lesson"])

            sync_quiz(session, lesson, lesson_bundle["quiz"])
            sync_flashcards(session, lesson, lesson_bundle["flashcards"])
