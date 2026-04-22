from prodik.application.interfaces.file import FileProcessingClient


class FileProcessingRegistry:
    _registry: dict[str, FileProcessingClient]

    def __init__(self) -> None:
        self._registry = {}

    def register(self, extension: str, client: FileProcessingClient) -> None:
        self._registry.update({extension: client})

    def get_client(self, extension: str) -> FileProcessingClient | None:
        return self._registry.get(extension)
