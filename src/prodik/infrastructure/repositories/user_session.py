from dataclasses import dataclass

import structlog
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import UserSessionRepository
from prodik.domain.credentials import IP, UserSession, UserSessionStatus
from prodik.domain.user import UserId

logger = structlog.get_logger()


@dataclass
class UserSessionRepositoryImpl(UserSessionRepository):
    session: AsyncSession

    async def revoke_all_by_user_id(self, id: UserId) -> None:
        await self.session.execute(
            update(UserSession)
            .where(UserSession.user_id == id)  # type: ignore
            .values(status=UserSessionStatus.REVOKED)
        )

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
        return list(result.scalars())

    async def create(self, user_session: UserSession) -> None:
        await self.session.execute(
            insert(UserSession).values(
                id=user_session.id,
                user_id=user_session.user_id,
                ip=user_session.ip,
                refresh_token=user_session.refresh_token,
                status=user_session.status,
                created_at=user_session.created_at,
                updated_at=user_session.updated_at,
            )
        )

    async def update(self, user_session: UserSession) -> None:
        await self.session.execute(
            update(UserSession)
            .where(UserSession.id == user_session.id)  # type: ignore
            .values(
                ip=user_session.ip,
                refresh_token=user_session.refresh_token,
                status=user_session.status,
                updated_at=user_session.updated_at,
            )
        )

    async def update_many(self, user_sessions: list[UserSession]) -> None:
        for s in user_sessions:
            await self.session.execute(
                update(UserSession)
                .where(UserSession.id == s.id)  # type: ignore
                .values(
                    status=s.status,
                    updated_at=s.updated_at,
                )
            )

    async def get_by_token(self, refresh_token: str) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession.refresh_token == refresh_token  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
