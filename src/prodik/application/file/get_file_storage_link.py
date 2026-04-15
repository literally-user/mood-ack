from dataclasses import dataclass

from prodik.application.errors import UserSessionRevokedError
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.identity_provider import IdentityProvider


@dataclass
class GetFileStorageLinkInteractor:
    file_storage_gateway: FileStorageGateway
    idp: IdentityProvider

    async def execute(self) -> str:
        current_user_session = await self.idp.get_current_session()
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")
        return await self.file_storage_gateway.get_storage_link()
