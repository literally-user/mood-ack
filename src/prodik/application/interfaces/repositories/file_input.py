from typing import Protocol

from prodik.domain.task import FileId, FileInput


class FileInputRepository(Protocol):
    async def create(self, input: FileInput) -> None: ...
    async def get_by_file_id(self, file_id: FileId) -> FileInput | None: ...
