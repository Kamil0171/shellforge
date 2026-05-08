from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import Quiz, QuizAnswer, QuizQuestion


router = APIRouter(prefix="/quiz", tags=["quizzes"])

templates = Jinja2Templates(directory="app/templates")


def get_quiz_data(session: Session, quiz_id: int):
    quiz = session.get(Quiz, quiz_id)

    if quiz is None:
        return None

    questions = session.exec(
        select(QuizQuestion)
        .where(QuizQuestion.quiz_id == quiz.id)
        .order_by(QuizQuestion.position)
    ).all()

    questions_data = []

    for question in questions:
        answers = session.exec(
            select(QuizAnswer).where(QuizAnswer.question_id == question.id)
        ).all()

        correct_answer = next(
            (answer.option_key for answer in answers if answer.is_correct),
            None,
        )

        questions_data.append(
            {
                "id": question.id,
                "text": question.text,
                "answers": [
                    {
                        "id": answer.option_key,
                        "text": answer.text,
                    }
                    for answer in answers
                ],
                "correct_answer": correct_answer,
            }
        )

    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "title": quiz.title,
        "description": quiz.description,
        "questions": questions_data,
    }


@router.get("/{quiz_id}")
def quiz_page(
    request: Request,
    quiz_id: int,
    session: Session = Depends(get_session),
):
    quiz = get_quiz_data(session, quiz_id)

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz nie został znaleziony.",
        )

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "quiz": quiz,
            "result": None,
            "selected_answers": {},
        },
    )


@router.post("/{quiz_id}")
async def check_quiz(
    request: Request,
    quiz_id: int,
    session: Session = Depends(get_session),
):
    quiz = get_quiz_data(session, quiz_id)

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz nie został znaleziony.",
        )

    form_data = await request.form()

    selected_answers = {}

    for question in quiz["questions"]:
        question_id = question["id"]
        selected_answers[question_id] = form_data.get(
            f"question_{question_id}",
            "",
        )

    correct_count = 0

    for question in quiz["questions"]:
        question_id = question["id"]

        if selected_answers.get(question_id) == question["correct_answer"]:
            correct_count += 1

    total_count = len(quiz["questions"])
    percentage = round((correct_count / total_count) * 100) if total_count else 0

    result = {
        "correct_count": correct_count,
        "total_count": total_count,
        "percentage": percentage,
    }

    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
        context={
            "quiz": quiz,
            "result": result,
            "selected_answers": selected_answers,
        },
    )