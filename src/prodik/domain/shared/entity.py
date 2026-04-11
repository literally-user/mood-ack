from typing import cast, override
from uuid import UUID


class Entity[EntityId: UUID]:
    id: EntityId

    @override
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Entity):
            return cast("bool", self.id == value.id)

        raise NotImplementedError

    @override
    def __hash__(self) -> int:
        return hash(self.id)
