from typing import Optional

from sqlmodel import Field, SQLModel


class LearningModule(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str


class Lesson(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    module_id: int = Field(foreign_key="learningmodule.id")
    title: str
    level: str
    duration: str
    description: str
    theory: str
    commands_json: str
    practice_task: str
    common_mistakes_json: str
    summary: str


class Quiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id")
    title: str
    description: str


class QuizQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    quiz_id: int = Field(foreign_key="quiz.id")
    text: str
    position: int


class QuizAnswer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_id: int = Field(foreign_key="quizquestion.id")
    text: str
    option_key: str
    is_correct: bool = False


class Flashcard(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lesson_id: int = Field(foreign_key="lesson.id")
    question: str
    answer: str
    position: int