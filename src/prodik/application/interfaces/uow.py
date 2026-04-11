from types import TracebackType
from typing import Protocol


class UoW(Protocol):
    async def __aenter__(self) -> None: ...
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None: ...
