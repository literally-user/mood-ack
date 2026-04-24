from dataclasses import dataclass

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import FileInputRepository
from prodik.domain.task.model import FileId, FileInput


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

    async def get_by_file_id(self, file_id: FileId) -> FileInput | None:
        stmt = select(FileInput).where(
            FileInput.file_id == file_id  # type: ignore
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
