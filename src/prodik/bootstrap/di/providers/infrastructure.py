from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    LocalAuthorizationRepositoryImpl,
    OAuthAuthorizationRepositoryImpl,
    TaskRepositoryImpl,
    UserRepositoryImpl,
    UserSessionRepositoryImpl,
)
from prodik.infrastructure.token_manager import (
    AccessTokenManagerImpl,
    OAuthTokenManagerImpl,
    RefreshTokenManagerImpl,
    StateTokenManagerImpl,
)
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[OAuthAuthorizationRepositoryImpl],
        WithParents[LocalAuthorizationRepositoryImpl],
        WithParents[UserSessionRepositoryImpl],
        WithParents[UserRepositoryImpl],
        WithParents[TaskRepositoryImpl],
        WithParents[PasswordHasherImpl],
        WithParents[AccessTokenManagerImpl],
        WithParents[RefreshTokenManagerImpl],
        WithParents[StateTokenManagerImpl],
        WithParents[OAuthTokenManagerImpl],
        WithParents[TransactionManagerImpl],
        scope=Scope.REQUEST,
    )
