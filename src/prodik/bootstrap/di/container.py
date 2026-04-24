from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from prodik.bootstrap.di.providers.application import ApplicationProvider
from prodik.bootstrap.di.providers.connection import (
    ConnectionProvider,
    S3Provider,
)
from prodik.bootstrap.di.providers.domain import DomainProvider
from prodik.bootstrap.di.providers.infrastructure import InfrastructureProvider
from prodik.bootstrap.di.providers.transport import HTTPXClientProvider
from prodik.infrastructure.config import (
    APIConfig,
    Config,
    KeyCloakConfig,
    ObjectStorageConfig,
    PersistenceConfig,
)


def get_async_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        DomainProvider(),
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
            Config: config,
        },
    )
