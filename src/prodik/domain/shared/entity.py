from dataclasses import dataclass
from typing import cast, override
from datetime import datetime
from uuid import UUID


@dataclass(kw_only=True)
class Entity[EntityId: UUID]:
    _id: EntityId
    _created_at: datetime
    _updated_at: datetime 

    @override
    def __eq__(self, value: object) -> bool:
        if isinstance(value, Entity):
            return cast("bool", self._id == value._id)

        return NotImplemented

    @override
    def __hash__(self) -> int:
        return hash(self._id)
