from typing import Protocol


class FileProcessingClient(Protocol):
    def process(self, content: str) -> str: ...
