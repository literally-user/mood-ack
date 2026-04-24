from dataclasses import dataclass

from prodik.application.errors import InvalidCredentialsError, UserSessionRevokedError
from prodik.application.interfaces.gateways import FileStorageGateway
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import UserSessionRepository
from prodik.domain.credentials import IP


@dataclass
class GetFileStorageLinkInteractor:
    user_session_repository: UserSessionRepository
    file_storage_gateway: FileStorageGateway
    idp: IdentityProvider

    async def execute(self, filename: str) -> str:
        current_user_meta = self.idp.get_user_meta()
        user_ip = self.idp.get_current_ip()

        current_user_session = await self.user_session_repository.get_by_user_id_and_ip(
            current_user_meta.user_id, IP(user_ip)
        )
        if current_user_session is None:
            raise InvalidCredentialsError("Invalid authorization header format")
        if current_user_session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")
        return await self.file_storage_gateway.get_storage_link(filename)
