from dataclasses import dataclass

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserSessionRepository
from prodik.domain.credentials import IP, UserSession, UserSessionStatus
from prodik.domain.user import UserId


@dataclass
class UserSessionRepositoryImpl(UserSessionRepository):
    session: AsyncSession

    async def revoke_all_by_user_id(self, id: UserId) -> None:
        stmt = (
            update(UserSession)
            .where(UserSession.user_id == id)  # type: ignore
            .values(status=UserSessionStatus.REVOKED)
        )
        await self.session.execute(stmt)

    async def get_by_user_id_and_ip(self, id: UserId, ip: IP) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.user_id == id,  # type: ignore
            UserSession.ip == ip,  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, id: UserId) -> list[UserSession]:
        stmt = select(UserSession).where(UserSession.user_id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, user_session: UserSession) -> None:
        self.session.add(user_session)

    async def update(self, user_session: UserSession) -> None:
        self.session.add(user_session)

    async def update_many(self, user_sessions: list[UserSession]) -> None:
        for session in user_sessions:
            self.session.add(session)
