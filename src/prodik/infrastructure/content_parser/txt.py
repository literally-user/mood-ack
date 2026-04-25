from prodik.application.interfaces.content_processing.content_parser import (
    ContentParserClient,
)


class TXTParserClient(ContentParserClient):
    def process(self, content: str) -> str:
        return content
