from prodik.application.interfaces.file import FileProcessingClient


class TXTProcessingClient(FileProcessingClient):
    def process(self, content: str) -> str:
        return content
