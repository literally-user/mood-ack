from dishka import Provider, Scope, WithParents, provide_all

from prodik.infrastructure.password_hasher import PasswordHasherImpl
from prodik.infrastructure.token_manager import TokenManagerImpl
from prodik.infrastructure.uow import UoWImpl


class InfrastructureProvider(Provider):
    provides = provide_all(
        WithParents[PasswordHasherImpl],
        WithParents[TokenManagerImpl],
        WithParents[UoWImpl],
        scope=Scope.REQUEST,
    )
