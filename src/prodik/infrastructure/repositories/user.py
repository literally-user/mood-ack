from dataclasses import dataclass

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserRepository
from prodik.domain.user import Email, User, UserId, Username


@dataclass
class UserRepositoryImpl(UserRepository):
    session: AsyncSession

    async def create(self, user: User) -> None:
        await self.session.execute(
            insert(User).values(
                id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                age=user.age,
                role=user.role,
                status=user.status,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )
        )

    async def update(self, user: User) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user.id)  # type: ignore
            .values(
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                age=user.age,
                role=user.role,
                status=user.status,
                updated_at=user.updated_at,
            )
        )

    async def delete(self, user: User) -> None:
        await self.session.execute(
            delete(User).where(User.id == user.id)  # type: ignore
        )

    async def get_by_uuid(self, id: UserId) -> User | None:
        stmt = select(User).where(User.id == id)  # type: ignore
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
        return list(result.scalars())
