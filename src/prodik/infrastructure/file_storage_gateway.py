import asyncio
from dataclasses import dataclass
from uuid import uuid4

from aiobotocore.client import AioBaseClient

from prodik.application.interfaces.gateways import FileMeta, FileStorageGateway
from prodik.domain.task import FileId
from prodik.infrastructure.config import ObjectStorageConfig


@dataclass(slots=True)
class FileStorageGatewayImpl(FileStorageGateway):
    client: AioBaseClient
    config: ObjectStorageConfig

    async def get_storage_link(self, filename: str) -> str:
        return await self.client.generate_presigned_url(  # type: ignore
            "put_object",
            Params={"Bucket": self.config.bucket, "Key": f"{uuid4()}+{filename}"},
            ExpiresIn=3600,
        )

    async def get_file_info(self, file_id: FileId) -> FileMeta | None:
        temp_directory = self.config.temp_directory

        await asyncio.to_thread(
            temp_directory.mkdir,
            parents=True,
            exist_ok=True,
        )

        file_path = temp_directory / str(file_id)

        await self.client.download_file(  # type: ignore
            self.config.bucket,
            str(file_id),
            str(file_path),
        )

        content = await asyncio.to_thread(file_path.read_text)

        return FileMeta(
            content=content,
            extension=str(file_id).split(".")[-1],
        )
