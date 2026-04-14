from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import OAuthAuthorizationRepository
from prodik.domain.credentials import OAuthAuthorization
from prodik.domain.user import UserId


@dataclass
class OAuthAuthorizationRepositoryImpl(OAuthAuthorizationRepository):
    session: AsyncSession

    async def get_by_user_id(self, user_id: UserId) -> OAuthAuthorization | None:
        stmt = select(OAuthAuthorization).where(
            OAuthAuthorization.user_id == user_id  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
