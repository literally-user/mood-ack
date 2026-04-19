from prodik.application.interfaces.auth import OAuthClient


class OAuthClientRegistry:
    _registry: dict[str, OAuthClient]

    def register(self, provider: str, client: OAuthClient) -> None:
        self._registry.update({provider: client})

    def get_client(self, provider: str) -> OAuthClient | None:
        return self._registry.get(provider)
