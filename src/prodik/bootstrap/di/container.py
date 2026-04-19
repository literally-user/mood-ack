from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from prodik.bootstrap.di.providers.application import ApplicationProvider
from prodik.bootstrap.di.providers.connection import (
    ConnectionProvider,
    S3Provider,
    HTTPXClientProvider,
)
from prodik.bootstrap.di.providers.infrastructure import InfrastructureProvider
from prodik.infrastructure.config import (
    APIConfig,
    Config,
    ObjectStorageConfig,
    PersistenceConfig,
    KeyCloakConfig,
)


def get_async_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        S3Provider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        ConnectionProvider(),
        HTTPXClientProvider(),
        context={
            APIConfig: config.api,
            PersistenceConfig: config.persistence,
            ObjectStorageConfig: config.object_storage,
            KeyCloakConfig: config.keycloak,
        },
    )
