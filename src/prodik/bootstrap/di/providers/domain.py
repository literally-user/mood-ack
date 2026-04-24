from dishka import Provider, Scope, provide

from prodik.domain.user.services import AccessControlService


class DomainProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def access_control_service(self) -> AccessControlService:
        return AccessControlService()
