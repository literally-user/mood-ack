from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider

from prodik.bootstrap.di.providers import (
    ApplicationProvider,
    ConnectionProvider,
    InfrastructureProvider,
)
from prodik.infrastructure.config import Config


def get_async_container(config: Config) -> AsyncContainer:
    return make_async_container(
        FastapiProvider(),
        InfrastructureProvider(),
        ApplicationProvider(),
        ConnectionProvider(),
        context={Config: config},
    )
