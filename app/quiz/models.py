from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.store.database.sqlalchemy_base import BaseModel


class ThemeModel(BaseModel):
    __tablename__ = "themes"

    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    
    questions: Mapped[list["QuestionModel"]] = relationship(
        "QuestionModel", back_populates="theme", cascade="all, delete-orphan"
    )


class QuestionModel(BaseModel):
    __tablename__ = "questions"

    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    theme_id: Mapped[int] = mapped_column(ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    
    theme: Mapped["ThemeModel"] = relationship("ThemeModel", back_populates="questions")
    answers: Mapped[list["AnswerModel"]] = relationship(
        "AnswerModel", back_populates="question", cascade="all, delete-orphan"
    )


class AnswerModel(BaseModel):
    __tablename__ = "answers"

    title: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[bool] = mapped_column(default=False, nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    
    question: Mapped["QuestionModel"] = relationship("QuestionModel", back_populates="answers")
