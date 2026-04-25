from dishka import Provider, Scope, WithParents, provide, provide_all

from prodik.infrastructure.content_parser import (
    ContentParserRegistry,
    TXTParserClient,
)
from prodik.infrastructure.file_storage_gateway import FileStorageGatewayImpl
from prodik.infrastructure.ml import PredictingModelImpl
from prodik.infrastructure.repositories import TaskRepositoryImpl
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class FileHandleProcessProvider(Provider):
    provides = provide_all(
        WithParents[TaskRepositoryImpl],
        WithParents[PredictingModelImpl],
        WithParents[FileStorageGatewayImpl],
        WithParents[TransactionManagerImpl],
        scope=Scope.REQUEST,
    )

    @provide(scope=Scope.REQUEST)
    def file_client_registry(self) -> ContentParserRegistry:
        registry = ContentParserRegistry()

        txt_client = TXTParserClient()

        registry.register("txt", txt_client)

        return registry
