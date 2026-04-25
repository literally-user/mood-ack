from dataclasses import dataclass
from uuid import uuid4

from aiobotocore.client import AioBaseClient

from prodik.application.interfaces.gateways import FileStorageGateway
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

    async def file_exists(self, file_id: FileId) -> bool:
        await self.client.head_object(  # type: ignore
            Bucket=self.config.bucket,
            Key=str(file_id),
        )
        return True

    async def download_file(self, file_id: FileId) -> None:
        await self.client.download_file(  # type: ignore
            self.config.bucket, str(file_id), str(self.config.temp_directory / file_id)
        )
