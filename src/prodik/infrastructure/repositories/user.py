from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Email, User, Username


@dataclass
class UserRepositoryImpl(UserRepository):
    session: AsyncSession

    async def create(self, user: User) -> None:
        self.session.add(user)

    async def delete(self, user: User) -> None:
        await self.session.delete(user)

    async def update(self, user: User) -> None:
        self.session.add(user)

    async def get_by_uuid(self, uuid: UUID) -> User | None:
        stmt = select(User).where(User.id == uuid)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: Email) -> User | None:
        stmt = select(User).where(User.email == email)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: Username) -> User | None:
        stmt = select(User).where(User.username == username)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int, size: int) -> list[User]:
        stmt = select(User).offset((page - 1) * size).limit(size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
