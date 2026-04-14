from sqlalchemy import (
    UUID,
    Column,
    Enum,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
)
from sqlalchemy.orm import registry

from prodik.domain.credentials import (
    LocalAuthorization,
    OAuthAuthorization,
    UserSession,
    UserSessionStatus,
)
from prodik.domain.task import Task, TaskState
from prodik.domain.user import User, UserRole, UserStatus

metadata = MetaData()
registry_mapper = registry(metadata=metadata)

user_account_table = Table(
    "user_account",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("username", String, nullable=False),
    Column("first_name", String, nullable=False),
    Column("last_name", String, nullable=False),
    Column("email", String, nullable=False),
    Column("age", Integer, nullable=False),
    Column("role", Enum(UserRole), nullable=False),
    Column("status", Enum(UserStatus), nullable=False),
)

user_session_table = Table(
    "user_session",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
    Column("ip", String(36), nullable=False),
    Column("refresh_token", String, nullable=False),
    Column("status", Enum(UserSessionStatus), nullable=False),
)

local_authorization_table = Table(
    "local_authorization",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
    Column("passowrd", String, nullable=False),
)

oauth_authorization_table = Table(
    "oauth_authorization",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
)

task_record_table = Table(
    "task_record",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("owner_id", UUID, ForeignKey("user_session.id"), nullable=False),
    Column("state", Enum(TaskState), nullable=False),
    Column("input", String, nullable=False),
    Column("result", Float, nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(
        User,
        user_account_table,
        properties={
            "_id": user_account_table.c.id,
        },
    )
    registry_mapper.map_imperatively(
        Task,
        task_record_table,
        properties={
            "_id": task_record_table.c.id,
        },
    )
    registry_mapper.map_imperatively(
        UserSession,
        user_session_table,
        properties={
            "_id": user_session_table.c.id,
        },
    )
    registry_mapper.map_imperatively(
        LocalAuthorization,
        local_authorization_table,
        properties={
            "_id": local_authorization_table.c.id,
        },
    )
    registry_mapper.map_imperatively(
        OAuthAuthorization,
        oauth_authorization_table,
        properties={
            "_id": oauth_authorization_table.c.id,
        },
    )
