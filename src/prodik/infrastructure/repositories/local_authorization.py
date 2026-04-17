from dataclasses import dataclass

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import LocalAuthorizationRepository
from prodik.domain.credentials import LocalAuthorization
from prodik.domain.user import UserId


@dataclass
class LocalAuthorizationRepositoryImpl(LocalAuthorizationRepository):
    session: AsyncSession

    async def create(self, local_authorization: LocalAuthorization) -> None:
        await self.session.execute(
            insert(LocalAuthorization).values(
                _id=local_authorization.id,
                _user_id=local_authorization.user_id,
                _password=local_authorization.password,
                _created_at=local_authorization.created_at,
                _updated_at=local_authorization.updated_at,
            )
        )

    async def update(self, local_authorization: LocalAuthorization) -> None:
        await self.session.execute(
            update(LocalAuthorization)
            .where(LocalAuthorization.id == local_authorization.id)  # type: ignore
            .values(
                _password=local_authorization.password,
            )
        )

    async def get_by_user_id(self, id: UserId) -> LocalAuthorization | None:
        stmt = select(LocalAuthorization).where(
            LocalAuthorization.user_id == id  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
