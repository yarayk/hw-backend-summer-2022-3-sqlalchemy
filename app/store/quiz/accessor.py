from collections.abc import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.base.base_accessor import BaseAccessor
from app.quiz.models import (
    AnswerModel,
    QuestionModel,
    ThemeModel,
)


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        session = self.app.database.session()
        async with session.begin():
            theme = ThemeModel(title=title)
            session.add(theme)
            await session.flush()
            await session.refresh(theme)
            return theme

    async def get_theme_by_title(self, title: str) -> ThemeModel | None:
        async with self.app.database.session() as session:
            stmt = select(ThemeModel).where(ThemeModel.title == title)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_theme_by_id(self, id_: int) -> ThemeModel | None:
        async with self.app.database.session() as session:
            stmt = select(ThemeModel).where(ThemeModel.id == id_)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_themes(self) -> Sequence[ThemeModel]:
        async with self.app.database.session() as session:
            stmt = select(ThemeModel)
            result = await session.execute(stmt)
            return result.scalars().all()

    async def create_question(
        self, title: str, theme_id: int, answers: Iterable[AnswerModel]
    ) -> QuestionModel:
        session = self.app.database.session()
        async with session.begin():
            question = QuestionModel(title=title, theme_id=theme_id)
            session.add(question)
            await session.flush()  # Get the ID without committing
            
            for answer in answers:
                answer.question_id = question.id
                session.add(answer)
            
            await session.refresh(question)
            # Load answers to avoid DetachedInstanceError
            await session.refresh(question, ["answers"])
            return question

    async def get_question_by_title(self, title: str) -> QuestionModel | None:
        async with self.app.database.session() as session:
            stmt = select(QuestionModel).where(QuestionModel.title == title)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def list_questions(
        self, theme_id: int | None = None
    ) -> Sequence[QuestionModel]:
        async with self.app.database.session() as session:
            if theme_id is not None:
                stmt = (
                    select(QuestionModel)
                    .where(QuestionModel.theme_id == theme_id)
                    .options(selectinload(QuestionModel.answers))
                )
            else:
                stmt = select(QuestionModel).options(selectinload(QuestionModel.answers))
            result = await session.execute(stmt)
            return result.scalars().all()
