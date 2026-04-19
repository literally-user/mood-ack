from typing import Protocol


class FileProcessingClient(Protocol):
    def process(self, content: str) -> str: ...


class FileProcessingRegistry:
    _registry: dict[str, FileProcessingClient]

    def register(self, extension: str, client: FileProcessingClient) -> None:
        self._registry.update({extension: client})

    def get_client(self, extension: str) -> FileProcessingClient | None:
        return self._registry.get(extension)
