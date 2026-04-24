from dishka import Provider, Scope, WithParents, provide, provide_all
from httpx import AsyncClient

from prodik.infrastructure.config import KeyCloakConfig
from prodik.infrastructure.content_processing import FileProcessorImpl, RawProcessorImpl
from prodik.infrastructure.file_storage_gateway import FileStorageGatewayImpl
from prodik.infrastructure.identity_provider import IdentityProviderImpl
from prodik.infrastructure.ml import PredictingModelImpl
from prodik.infrastructure.oauth.keycloak import KeycloakOAuthClient
from prodik.infrastructure.oauth.registry import OAuthClientRegistry
from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.repositories import (
    FileInputRepositoryImpl,
    LocalAuthorizationRepositoryImpl,
    OAuthAuthorizationRepositoryImpl,
    RawInputRepositoryImpl,
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
        WithParents[IdentityProviderImpl],
        WithParents[PredictingModelImpl],
        WithParents[FileStorageGatewayImpl],
        WithParents[RawInputRepositoryImpl],
        WithParents[FileInputRepositoryImpl],
        WithParents[FileProcessorImpl],
        WithParents[RawProcessorImpl],
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def oauth_registry(
        self, transport: AsyncClient, keycloak_config: KeyCloakConfig
    ) -> OAuthClientRegistry:
        registry = OAuthClientRegistry()

        keycloak_client = KeycloakOAuthClient(keycloak_config, transport)

        registry.register("keycloak", keycloak_client)

        return registry
