from prodik.application.interfaces.file import ContentParserClient


class TXTParserClient(ContentParserClient):
    def process(self, content: str) -> str:
        return content
