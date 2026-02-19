from hashlib import sha256
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.admin.models import AdminModel
from app.base.base_accessor import BaseAccessor

if TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        admin = await self.get_by_email(app.config.admin.email)
        if not admin:
            hashed_password = sha256(app.config.admin.password.encode()).hexdigest()
            await self.create_admin(app.config.admin.email, hashed_password)

    async def get_by_email(self, email: str) -> AdminModel | None:
        session = self.app.database.session()
        async with session:
            stmt = select(AdminModel).where(AdminModel.email == email)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def create_admin(self, email: str, password: str) -> AdminModel:
        session = self.app.database.session()
        async with session.begin():
            admin = AdminModel(email=email, password=password)
            session.add(admin)
            await session.flush()
            await session.refresh(admin)
            return admin
