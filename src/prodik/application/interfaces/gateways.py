from dataclasses import dataclass
from typing import Protocol

from prodik.domain.task import FileId


@dataclass(frozen=True, slots=True, kw_only=True)
class FileMeta:
    extension: str


class FileStorageGateway(Protocol):
    async def get_storage_link(self, filename: str) -> str: ...
    async def file_exists(self, file_id: FileId) -> bool: ...
    async def download_file(self, file_id: FileId) -> None: ...
