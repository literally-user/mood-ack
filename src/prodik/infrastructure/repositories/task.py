from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import TaskRepository
from prodik.domain.task import Task, TaskId
from prodik.domain.user import UserId


@dataclass
class TaskRepositoryImpl(TaskRepository):
    session: AsyncSession

    async def create(self, task: Task) -> None:
        self.session.add(task)

    async def update(self, task: Task) -> None:
        self.session.add(task)

    async def get_by_id(self, id: TaskId) -> Task | None:
        stmt = select(Task).where(Task.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int, size: int) -> list[Task]:
        stmt = select(Task).offset((page - 1) * size).limit(size)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_all_by_user_id(
        self, user_id: UserId, page: int, size: int
    ) -> list[Task]:
        stmt = (
            select(Task)
            .where(Task.owner_id == user_id)  # type: ignore
            .offset((page - 1) * size)
            .limit(size)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
