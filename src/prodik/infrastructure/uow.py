from types import TracebackType
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.transaction_manager import TransactionManager


class UoWImpl(TransactionManager):
    _session: AsyncSession

    @override
    async def __aenter__(self) -> None: ...

    @override
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        if exc:
            await self._session.commit()
            return
        await self._session.rollback()
