from dishka import Provider, Scope, provide
from httpx import AsyncClient


class HTTPXClientProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def client(self) -> AsyncClient:
        async with AsyncClient() as client:
            return client
