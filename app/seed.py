import json

from sqlmodel import Session, select

from app.content.terminal_navigation import TERMINAL_NAVIGATION
from app.database import engine
from app.models import Flashcard, LearningModule, Lesson, Quiz, QuizAnswer, QuizQuestion


LESSONS = [
    TERMINAL_NAVIGATION,
]


def get_or_create_module(session, module_data):
    module = session.exec(
        select(LearningModule).where(LearningModule.title == module_data["title"])
    ).first()

    if module:
        return module

    module = LearningModule(
        title=module_data["title"],
        description=module_data["description"],
    )

    session.add(module)
    session.commit()
    session.refresh(module)

    return module


def get_or_create_lesson(session, module, lesson_data):
    lesson = session.exec(
        select(Lesson).where(
            Lesson.module_id == module.id,
            Lesson.title == lesson_data["title"],
        )
    ).first()

    if lesson:
        return lesson

    lesson = Lesson(
        module_id=module.id,
        title=lesson_data["title"],
        level=lesson_data["level"],
        duration=lesson_data["duration"],
        description=lesson_data["description"],
        theory=lesson_data["theory"],
        commands_json=json.dumps(lesson_data["commands"], ensure_ascii=False),
        practice_task=lesson_data["practice_task"],
        common_mistakes_json=json.dumps(
            lesson_data["common_mistakes"],
            ensure_ascii=False,
        ),
        summary=lesson_data["summary"],
    )

    session.add(lesson)
    session.commit()
    session.refresh(lesson)

    return lesson


def sync_quiz(session, lesson, quiz_data):
    quiz = session.exec(
        select(Quiz).where(Quiz.lesson_id == lesson.id)
    ).first()

    if not quiz:
        quiz = Quiz(
            lesson_id=lesson.id,
            title=quiz_data["title"],
            description=quiz_data["description"],
        )

        session.add(quiz)
        session.commit()
        session.refresh(quiz)

    existing_questions = session.exec(
        select(QuizQuestion).where(QuizQuestion.quiz_id == quiz.id)
    ).all()

    if len(existing_questions) == len(quiz_data["questions"]):
        return quiz

    for question in existing_questions:
        existing_answers = session.exec(
            select(QuizAnswer).where(QuizAnswer.question_id == question.id)
        ).all()

        for answer in existing_answers:
            session.delete(answer)

        session.delete(question)

    session.commit()

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

    if len(existing_flashcards) == len(flashcards_data):
        return

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
            module = get_or_create_module(session, lesson_bundle["module"])
            lesson = get_or_create_lesson(session, module, lesson_bundle["lesson"])

            sync_quiz(session, lesson, lesson_bundle["quiz"])
            sync_flashcards(session, lesson, lesson_bundle["flashcards"])