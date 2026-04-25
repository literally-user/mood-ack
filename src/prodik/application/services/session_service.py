from dataclasses import dataclass

from prodik.application.auth.errors import (
    InvalidCredentialsError,
    UserSessionRevokedError,
)
from prodik.application.interfaces.identity_provider import IdentityProvider
from prodik.application.interfaces.repositories import (
    UserRepository,
    UserSessionRepository,
)
from prodik.domain.credentials import IP, UserSession
from prodik.domain.user import User


@dataclass
class AuthorizedMeta:
    user: User
    session: UserSession


@dataclass
class SessionService:
    idp: IdentityProvider
    user_session_repository: UserSessionRepository
    user_repository: UserRepository

    async def get_authorized_meta(self) -> AuthorizedMeta:
        meta = self.idp.get_user_meta()
        ip = self.idp.get_current_ip()

        session = await self.user_session_repository.get_by_user_id_and_ip(
            meta.user_id, IP(ip)
        )
        if session is None:
            raise InvalidCredentialsError("Invalid authorization header format")

        if session.is_revoked():
            raise UserSessionRevokedError("Session was revoked")

        user = await self.user_repository.get_by_uuid(meta.user_id)
        if user is None:
            raise InvalidCredentialsError("Invalid credentials")

        return AuthorizedMeta(
            user=user,
            session=session,
        )
