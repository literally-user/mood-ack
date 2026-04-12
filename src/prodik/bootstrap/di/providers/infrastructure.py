from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.token_manager import (
    AccessTokenManagerImpl,
    OAuthTokenManagerImpl,
    RefreshTokenManagerImpl,
    StateTokenManagerImpl,
)
from prodik.infrastructure.uow import UoWImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[PasswordHasherImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[StateTokenManagerImpl],
        WithParents[OAuthTokenManagerImpl],
        WithParents[UoWImpl],
        scope=Scope.REQUEST,
    )
