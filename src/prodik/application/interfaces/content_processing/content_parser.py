from typing import Protocol


class ContentParserClient(Protocol):
    def process(self, content: str) -> str: ...
