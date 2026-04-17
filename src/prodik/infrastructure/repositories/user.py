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
                _id=user.id,
                _username=user.username,
                _first_name=user.first_name,
                _last_name=user.last_name,
                _email=user.email,
                _age=user.age,
                _role=user.role,
                _status=user.status,
                _created_at=user.created_at,
                _updated_at=user.updated_at,
            )
        )

    async def update(self, user: User) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user.id)  # type: ignore
            .values(
                _username=user.username,
                _first_name=user.first_name,
                _last_name=user.last_name,
                _email=user.email,
                _age=user.age,
                _role=user.role,
                _status=user.status,
                _updated_at=user.updated_at,
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
