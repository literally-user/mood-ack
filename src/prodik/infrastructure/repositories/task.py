from dataclasses import dataclass

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from prodik.application.interfaces.repositories import TaskRepository
from prodik.domain.task import Task, TaskId
from prodik.domain.user import UserId


@dataclass
class TaskRepositoryImpl(TaskRepository):
    session: AsyncSession

    async def create(self, task: Task) -> None:
        await self.session.execute(
            insert(Task).values(
                id=task.id,
                owner_id=task.owner_id,
                state=task.state,
                input_type=task.input_type,
                input_id=task.input_id,
                result=task.result.value if task.result else None,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )
        )

    async def update(self, task: Task) -> None:
        await self.session.execute(
            update(Task)
            .where(Task.id == task.id)  # type: ignore
            .values(
                owner_id=task.owner_id,
                state=task.state,
                input_type=task.input_type,
                input_id=task.input_id,
                result=task.result or None,
                updated_at=task.updated_at,
            )
        )

    async def get_by_id(self, id: TaskId) -> Task | None:
        stmt = select(Task).where(Task.id == id)  # type: ignore
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete(self, task: Task) -> None:
        await self.session.execute(
            delete(Task).where(Task.id == task.id)  # type: ignore
        )

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
