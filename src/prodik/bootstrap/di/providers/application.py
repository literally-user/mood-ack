from dishka import Provider, Scope, provide_all


class ApplicationProvider(Provider):
    provides = provide_all(scope=Scope.REQUEST)
