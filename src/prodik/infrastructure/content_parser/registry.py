from prodik.application.interfaces.content_processing.content_parser import (
    ContentParserClient,
)


class ContentParserRegistry:
    _registry: dict[str, ContentParserClient]

    def __init__(self) -> None:
        self._registry = {}

    def register(self, extension: str, client: ContentParserClient) -> None:
        self._registry.update({extension: client})

    def get_client(self, extension: str) -> ContentParserClient | None:
        return self._registry.get(extension)
