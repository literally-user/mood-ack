from dishka import Provider, Scope, WithParents, provide_all, provide
from httpx import AsyncClient

from prodik.infrastructure.file_storage_gateway import FileStorageGatewayImpl
from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.ml import PredictingModelImpl
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.registries import FileProcessingRegistry
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
from prodik.infrastructure.oauth.registry import OAuthClientRegistry
from prodik.infrastructure.oauth.keycloak import KeycloakOAuthClient
from prodik.infrastructure.transaction_manager import TransactionManagerImpl
from prodik.infrastructure.config import KeyCloakConfig

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
        WithParents[FileProcessingRegistry],
        WithParents[IdentityProviderImpl],
        WithParents[PredictingModelImpl],
        WithParents[FileStorageGatewayImpl],
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def oauth_registry(self, transport: AsyncClient, keycloak_config: KeyCloakConfig) -> OAuthClientRegistry:
        registry = OAuthClientRegistry()

        keycloak_client = KeycloakOAuthClient(keycloak_config, transport)

        registry.register("keycloak", keycloak_client)

        return registry