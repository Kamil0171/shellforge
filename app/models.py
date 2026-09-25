from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Text
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


class DynamicIncidentSession(SQLModel, table=True):
    __tablename__ = "dynamic_incident_session"

    session_id: str = Field(primary_key=True, max_length=36)
    scenario_id: str = Field(index=True, max_length=36)
    status: str = Field(index=True, max_length=16)
    revision: int = Field(ge=0)
    schema_version: int = Field(ge=1)
    snapshot_json: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None
    expires_at: datetime = Field(index=True)
