from dataclasses import dataclass

from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.services import SessionService


@dataclass
class GetFileStorageLinkInteractor:
    file_storage_gateway: FileStorageGateway
    session_service: SessionService

    async def execute(self, filename: str) -> str:
        await self.session_service.get_authorized_meta()
        return await self.file_storage_gateway.get_storage_link(filename)
