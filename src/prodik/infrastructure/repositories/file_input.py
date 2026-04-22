from dataclasses import dataclass

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import FileInputRepository
from prodik.domain.task.model import FileInput


@dataclass
class FileInputRepositoryImpl(FileInputRepository):
    session: AsyncSession

    async def create(self, input: FileInput) -> None:
        await self.session.execute(
            insert(FileInput).values(
                id=input.id,
                file_id=input.file_id,
                created_at=input.created_at,
                updated_at=input.updated_at,
            )
        )
