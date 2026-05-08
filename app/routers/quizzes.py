from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/quiz", tags=["quizzes"])

templates = Jinja2Templates(directory="app/templates")


quizzes_data = {
    1: {
        "id": 1,
        "lesson_id": 1,
        "title": "Quiz: pwd, ls i cd",
        "description": "Sprawdź, czy rozumiesz podstawowe komendy poruszania się po terminalu.",
        "questions": [
            {
                "id": 1,
                "text": "Do czego służy komenda pwd?",
                "answers": [
                    {"id": "a", "text": "Do usuwania katalogów"},
                    {"id": "b", "text": "Do wyświetlania aktualnego katalogu roboczego"},
                    {"id": "c", "text": "Do tworzenia nowych użytkowników"},
                    {"id": "d", "text": "Do restartowania systemu"},
                ],
                "correct_answer": "b",
            },
            {
                "id": 2,
                "text": "Która komenda wyświetla zawartość katalogu?",
                "answers": [
                    {"id": "a", "text": "ls"},
                    {"id": "b", "text": "cd"},
                    {"id": "c", "text": "pwd"},
                    {"id": "d", "text": "mkdir"},
                ],
                "correct_answer": "a",
            },
            {
                "id": 3,
                "text": "Co robi komenda cd ..?",
                "answers": [
                    {"id": "a", "text": "Przechodzi do katalogu domowego"},
                    {"id": "b", "text": "Usuwa aktualny katalog"},
                    {"id": "c", "text": "Przechodzi katalog wyżej"},
                    {"id": "d", "text": "Wyświetla pliki ukryte"},
                ],
                "correct_answer": "c",
            },
            {
                "id": 4,
                "text": "Która komenda przechodzi do katalogu domowego użytkownika?",
                "answers": [
                    {"id": "a", "text": "cd /"},
                    {"id": "b", "text": "cd home"},
                    {"id": "c", "text": "cd ~"},
                    {"id": "d", "text": "pwd ~"},
                ],
                "correct_answer": "c",
            },
        ],
    }
}


@router.get("/{quiz_id}")
def quiz_page(request: Request, quiz_id: int):
    quiz = quizzes_data.get(quiz_id)

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
def check_quiz(
    request: Request,
    quiz_id: int,
    question_1: str = Form(default=""),
    question_2: str = Form(default=""),
    question_3: str = Form(default=""),
    question_4: str = Form(default=""),
):
    quiz = quizzes_data.get(quiz_id)

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz nie został znaleziony.",
        )

    selected_answers = {
        1: question_1,
        2: question_2,
        3: question_3,
        4: question_4,
    }

    correct_count = 0

    for question in quiz["questions"]:
        question_id = question["id"]
        if selected_answers.get(question_id) == question["correct_answer"]:
            correct_count += 1

    total_count = len(quiz["questions"])
    percentage = round((correct_count / total_count) * 100)

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