from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
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
from prodik.domain.task import FileInput, InputType, RawInput, Task, TaskState
from prodik.domain.user import (
    User,
    UserRole,
    UserStatus,
)
from prodik.infrastructure.db.types import (
    AgeType,
    EmailType,
    FirstNameType,
    IPType,
    LastNameType,
    TaskResultType,
    UsernameType,
)

metadata = MetaData()
registry_mapper = registry(metadata=metadata)


user_account_table = Table(
    "user_account",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("username", UsernameType(), nullable=False),
    Column("first_name", FirstNameType(), nullable=False),
    Column("last_name", LastNameType(), nullable=False),
    Column("email", EmailType(), nullable=False),
    Column("age", AgeType(), nullable=False),
    Column("role", Enum(UserRole), nullable=False),
    Column("status", Enum(UserStatus), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

user_session_table = Table(
    "user_session",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column(
        "user_id",
        UUID,
        ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("ip", IPType(), nullable=False),
    Column("refresh_token", String, nullable=False),
    Column("status", Enum(UserSessionStatus), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

local_authorization_table = Table(
    "local_authorization",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column(
        "user_id",
        UUID(as_uuid=True),
        ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("password", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

oauth_authorization_table = Table(
    "oauth_authorization",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

task_record_table = Table(
    "task_record",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column(
        "owner_id",
        UUID(as_uuid=True),
        ForeignKey("user_account.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("state", Enum(TaskState), nullable=False),
    Column("input_type", Enum(InputType), nullable=False),
    Column("input_id", UUID(as_uuid=True), nullable=False),
    Column("result", TaskResultType, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

raw_input_table = Table(
    "raw_input_record",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("content", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

file_input_table = Table(
    "file_input_record",
    metadata,
    Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
    Column("file_id", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(
        User,
        user_account_table,
    )
    registry_mapper.map_imperatively(
        Task,
        task_record_table,
    )
    registry_mapper.map_imperatively(
        UserSession,
        user_session_table,
    )
    registry_mapper.map_imperatively(
        LocalAuthorization,
        local_authorization_table,
    )
    registry_mapper.map_imperatively(
        OAuthAuthorization,
        oauth_authorization_table,
    )
    registry_mapper.map_imperatively(
        RawInput,
        raw_input_table,
    )
    registry_mapper.map_imperatively(
        FileInput,
        file_input_table,
    )
