from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.ml import PredictingModelImpl
from prodik.infrastructure.repositories import TaskRepositoryImpl
from prodik.infrastructure.transaction_manager import TransactionManagerImpl


class RawHandleProcessProvider(Provider):
    provides = provide_all(
        WithParents[TaskRepositoryImpl],
        WithParents[PredictingModelImpl],
        WithParents[TransactionManagerImpl],
        scope=Scope.REQUEST,
    )
