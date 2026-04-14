from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuthorizationRepository
from prodik.domain.credentials import LocalAuthorization
from prodik.domain.user import UserId


@dataclass
class LocalAuthorizationRepositoryImpl(LocalAuthorizationRepository):
    session: AsyncSession

    async def create(self, local_authorization: LocalAuthorization) -> None:
        self.session.add(local_authorization)

    async def update(self, local_authorization: LocalAuthorization) -> None:
        self.session.add(local_authorization)

    async def get_by_user_id(self, id: UserId) -> LocalAuthorization:
        stmt = select(LocalAuthorization).where(LocalAuthorization.user_id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one()
