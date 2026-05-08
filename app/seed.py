import json

from sqlmodel import Session, select

from app.database import engine
from app.models import LearningModule, Lesson, Quiz, QuizAnswer, QuizQuestion


def seed_database():
    with Session(engine) as session:
        existing_module = session.exec(
            select(LearningModule).where(LearningModule.title == "Podstawy terminala")
        ).first()

        if existing_module:
            return

        module = LearningModule(
            title="Podstawy terminala",
            description="Pierwszy moduł poświęcony pracy w terminalu Linux.",
        )

        session.add(module)
        session.commit()
        session.refresh(module)

        lesson = Lesson(
            module_id=module.id,
            title="Gdzie jestem? Komendy pwd, ls i cd",
            level="Podstawowy",
            duration="20 min",
            description=(
                "Poznasz podstawowe komendy do sprawdzania aktualnego katalogu, "
                "wyświetlania plików oraz poruszania się po systemie plików."
            ),
            theory=(
                "Terminal pozwala wykonywać polecenia tekstowe w systemie Linux. "
                "Jedną z pierwszych umiejętności jest poruszanie się po systemie plików. "
                "System plików można wyobrazić sobie jako drzewo katalogów. "
                "Użytkownik znajduje się zawsze w jakimś aktualnym katalogu roboczym."
            ),
            commands_json=json.dumps(
                [
                    {
                        "command": "pwd",
                        "description": "Wyświetla aktualny katalog roboczy.",
                        "example": "$ pwd\n/home/student",
                    },
                    {
                        "command": "ls",
                        "description": "Wyświetla pliki i katalogi w bieżącym katalogu.",
                        "example": "$ ls\nDocuments Downloads Pictures",
                    },
                    {
                        "command": "ls -la",
                        "description": "Wyświetla szczegółową listę plików, także ukrytych.",
                        "example": "$ ls -la\n-rw-r--r-- 1 student student 120 notes.txt",
                    },
                    {
                        "command": "cd Documents",
                        "description": "Przechodzi do katalogu Documents.",
                        "example": "$ cd Documents",
                    },
                    {
                        "command": "cd ..",
                        "description": "Przechodzi katalog wyżej.",
                        "example": "$ cd ..",
                    },
                    {
                        "command": "cd ~",
                        "description": "Przechodzi do katalogu domowego użytkownika.",
                        "example": "$ cd ~",
                    },
                ],
                ensure_ascii=False,
            ),
            practice_task=(
                "Otwórz terminal i wykonaj kolejno: <code>pwd</code>, <code>ls</code>, "
                "<code>cd Documents</code>, <code>pwd</code>, <code>cd ..</code>, "
                "<code>pwd</code>, <code>cd ~</code>, <code>pwd</code>. "
                "Zwróć uwagę, jak zmienia się aktualny katalog roboczy."
            ),
            common_mistakes_json=json.dumps(
                [
                    "Wpisanie <code>cdDocuments</code> zamiast <code>cd Documents</code>.",
                    "Mylenie komendy <code>pwd</code> z <code>cd</code>.",
                    "Próba wejścia do katalogu, który nie istnieje.",
                    "Nieuwzględnianie wielkości liter w nazwach katalogów.",
                ],
                ensure_ascii=False,
            ),
            summary=(
                "Komendy <code>pwd</code>, <code>ls</code> i <code>cd</code> są podstawą pracy "
                "w terminalu. Dzięki nim wiesz, gdzie jesteś, co znajduje się w katalogu "
                "i jak przechodzić między katalogami."
            ),
        )

        session.add(lesson)
        session.commit()
        session.refresh(lesson)

        quiz = Quiz(
            lesson_id=lesson.id,
            title="Quiz: pwd, ls i cd",
            description="Sprawdź, czy rozumiesz podstawowe komendy poruszania się po terminalu.",
        )

        session.add(quiz)
        session.commit()
        session.refresh(quiz)

        questions_data = [
            {
                "text": "Do czego służy komenda pwd?",
                "answers": [
                    ("a", "Do usuwania katalogów", False),
                    ("b", "Do wyświetlania aktualnego katalogu roboczego", True),
                    ("c", "Do tworzenia nowych użytkowników", False),
                    ("d", "Do restartowania systemu", False),
                ],
            },
            {
                "text": "Która komenda wyświetla zawartość katalogu?",
                "answers": [
                    ("a", "ls", True),
                    ("b", "cd", False),
                    ("c", "pwd", False),
                    ("d", "mkdir", False),
                ],
            },
            {
                "text": "Co robi komenda cd ..?",
                "answers": [
                    ("a", "Przechodzi do katalogu domowego", False),
                    ("b", "Usuwa aktualny katalog", False),
                    ("c", "Przechodzi katalog wyżej", True),
                    ("d", "Wyświetla pliki ukryte", False),
                ],
            },
            {
                "text": "Która komenda przechodzi do katalogu domowego użytkownika?",
                "answers": [
                    ("a", "cd /", False),
                    ("b", "cd home", False),
                    ("c", "cd ~", True),
                    ("d", "pwd ~", False),
                ],
            },
        ]

        for index, question_data in enumerate(questions_data, start=1):
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