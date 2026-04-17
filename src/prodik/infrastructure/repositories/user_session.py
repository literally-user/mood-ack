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
            .where(UserSession._user_id == id)  # type: ignore
            .values(_status=UserSessionStatus.REVOKED)
        )

    async def get_by_user_id_and_ip(self, id: UserId, ip: IP) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession._user_id == id,  # type: ignore
            UserSession._ip == ip,  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_user_id(self, id: UserId) -> list[UserSession]:
        stmt = select(UserSession).where(UserSession._user_id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return list(result.scalars())

    async def create(self, user_session: UserSession) -> None:
        await self.session.execute(
            insert(UserSession).values(
                _id=user_session._id,
                _user_id=user_session._user_id,
                _ip=user_session._ip,
                _refresh_token=user_session._refresh_token,
                _status=user_session._status,
                _created_at=user_session._created_at,
                _updated_at=user_session._updated_at,
            )
        )

    async def update(self, user_session: UserSession) -> None:
        await self.session.execute(
            update(UserSession)
            .where(UserSession._id == user_session._id)  # type: ignore
            .values(
                _ip=user_session._ip,
                _refresh_token=user_session._refresh_token,
                _status=user_session._status,
                _updated_at=user_session._updated_at,
            )
        )

    async def update_many(self, user_sessions: list[UserSession]) -> None:
        for s in user_sessions:
            await self.session.execute(
                update(UserSession)
                .where(UserSession._id == s._id)  # type: ignore
                .values(
                    _status=s._status,
                    _updated_at=s._updated_at,
                )
            )

    async def get_by_token(self, refresh_token: str) -> UserSession | None:
        stmt = select(UserSession).where(
            UserSession._refresh_token == refresh_token  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
