from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from aiobotocore.client import AioBaseClient
from aiobotocore.response import StreamingBody

from prodik.application.interfaces.gateways import FileMeta, FileStorageGateway
from prodik.domain.task import FileId
from prodik.infrastructure.config import ObjectStorageConfig


@dataclass(slots=True)
class FileStorageGatewayImpl(FileStorageGateway):
    client: AioBaseClient
    config: ObjectStorageConfig

    async def get_storage_link(self) -> str:
        file_id = uuid4()
        key: str = str(file_id)

        return self.client.generate_presigned_url(  # type: ignore
            ClientMethod="put_object",
            Params={
                "Bucket": self.config.bucket,
                "Key": key,
            },
            ExpiresIn=3600,
        )

    async def get_file_info(self, file_id: FileId) -> FileMeta | None:
        key: str = str(file_id)

        try:
            response: dict[str, Any] = await self.client.get_object(  # type: ignore
                Bucket=self.config.bucket,
                Key=key,
            )

            body: StreamingBody = response["Body"]
            raw: bytes = await body.read()
            content: str = raw.decode("utf-8")

            return FileMeta(
                content=content,
                extension=key.rsplit(".", maxsplit=1)[-1] if "." in key else "",
            )

        except self.client.exceptions.NoSuchKey:  # type: ignore
            return None
