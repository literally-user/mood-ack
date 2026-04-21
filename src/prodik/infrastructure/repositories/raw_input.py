from dataclasses import dataclass

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import RawInputRepository
from prodik.domain.task.model import RawInput


@dataclass
class RawInputRepositoryImpl(RawInputRepository):
    session: AsyncSession

    async def create(self, input: RawInput) -> None:
        await self.session.execute(
            insert(RawInput).values(
                id=input.id,
                content=input.content,
                created_at=input.created_at,
                updated_at=input.updated_at,
            )
        )
