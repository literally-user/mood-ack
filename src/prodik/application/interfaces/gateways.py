from dataclasses import dataclass
from typing import Protocol

from prodik.domain.task import FileId


@dataclass(frozen=True, slots=True, kw_only=True)
class FileMeta:
    content: str
    extension: str


class FileStorageGateway(Protocol):
    async def get_storage_link(self, filename: str) -> str: ...
    async def get_file_info(self, file_id: FileId) -> FileMeta | None: ...
