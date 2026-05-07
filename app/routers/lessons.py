from fastapi import APIRouter, HTTPException, Request
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/lessons", tags=["lessons"])

templates = Jinja2Templates(directory="app/templates")


lessons_data = [
    {
        "id": 1,
        "title": "Gdzie jestem? Komendy pwd, ls i cd",
        "module": "Podstawy terminala",
        "level": "Podstawowy",
        "duration": "20 min",
        "description": (
            "Poznasz podstawowe komendy do sprawdzania aktualnego katalogu, "
            "wyświetlania plików oraz poruszania się po systemie plików."
        ),
        "theory": (
            "Terminal pozwala wykonywać polecenia tekstowe w systemie Linux. "
            "Jedną z pierwszych umiejętności jest poruszanie się po systemie plików. "
            "System plików można wyobrazić sobie jako drzewo katalogów. "
            "Użytkownik znajduje się zawsze w jakimś aktualnym katalogu roboczym."
        ),
        "commands": [
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
        "practice_task": (
            "Otwórz terminal i wykonaj kolejno: <code>pwd</code>, <code>ls</code>, "
            "<code>cd Documents</code>, <code>pwd</code>, <code>cd ..</code>, "
            "<code>pwd</code>, <code>cd ~</code>, <code>pwd</code>. "
            "Zwróć uwagę, jak zmienia się aktualny katalog roboczy."
        ),
        "common_mistakes": [
            "Wpisanie <code>cdDocuments</code> zamiast <code>cd Documents</code>.",
            "Mylenie komendy <code>pwd</code> z <code>cd</code>.",
            "Próba wejścia do katalogu, który nie istnieje.",
            "Nieuwzględnianie wielkości liter w nazwach katalogów.",
        ],
        "summary": (
            "Komendy <code>pwd</code>, <code>ls</code> i <code>cd</code> są podstawą pracy "
            "w terminalu. Dzięki nim wiesz, gdzie jesteś, co znajduje się w katalogu "
            "i jak przechodzić między katalogami."
        ),
    }
]


@router.get("/")
def lessons_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="lessons.html",
        context={
            "lessons": lessons_data,
        },
    )


@router.get("/{lesson_id}")
def lesson_detail_page(request: Request, lesson_id: int):
    lesson = next(
        (item for item in lessons_data if item["id"] == lesson_id),
        None,
    )

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lekcja nie została znaleziona.",
        )

    return templates.TemplateResponse(
        request=request,
        name="lesson_detail.html",
        context={
            "lesson": lesson,
        },
    )