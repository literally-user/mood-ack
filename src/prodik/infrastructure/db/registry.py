from typing import Any, override

from sqlalchemy import (
    UUID,
    Column,
    DateTime,
    Dialect,
    Enum,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    TypeDecorator,
)
from sqlalchemy.orm import registry

from prodik.domain.credentials import (
    IP,
    LocalAuthorization,
    OAuthAuthorization,
    UserSession,
    UserSessionStatus,
)
from prodik.domain.task import InputType, Task, TaskState
from prodik.domain.user import (
    Age,
    Email,
    FirstName,
    LastName,
    User,
    Username,
    UserRole,
    UserStatus,
)

metadata = MetaData()
registry_mapper = registry(metadata=metadata)


class UsernameType(TypeDecorator[Username]):
    impl = String
    cache_ok = True

    def process_bind_param(
        self,
        value: Username | None,
        dialect: Dialect,
    ) -> str | None:
        if value is None:
            return None

        return value.value

    def process_result_value(
        self,
        value: str | None,
        dialect: Dialect,
    ) -> Username | None:
        if value is None:
            return None

        return Username(value)


class FirstNameType(TypeDecorator[FirstName]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: FirstName | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> FirstName | None:
        if value is None:
            return None

        return FirstName(value)


class LastNameType(TypeDecorator[LastName]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: LastName | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(
        self, value: Any | None, dialect: Dialect
    ) -> LastName | None:
        if value is None:
            return None

        return LastName(value)


class EmailType(TypeDecorator[Email]):
    impl = String
    cache_ok = True

    @override
    def process_bind_param(self, value: Email | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    @override
    def process_result_value(self, value: Any | None, dialect: Dialect) -> Email | None:
        if value is None:
            return None

        return Email(value)


class AgeType(TypeDecorator[Age]):
    impl = Integer
    cache_ok = True

    def process_bind_param(self, value: Age | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    def process_result_value(self, value: Any | None, dialect: Dialect) -> Age | None:
        if value is None:
            return None

        return Age(value)


class IPType(TypeDecorator[IP]):
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value: IP | None, dialect: Dialect) -> Any:
        if value is None:
            return None

        return value.value

    def process_result_value(self, value: Any | None, dialect: Dialect) -> IP | None:
        if value is None:
            return None

        return IP(value)


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
    Column("user_id", UUID, ForeignKey("user_account.id"), nullable=False),
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
        "user_id", UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=False
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
        "owner_id", UUID(as_uuid=True), ForeignKey("user_account.id"), nullable=False
    ),
    Column("state", Enum(TaskState), nullable=False),
    Column("input_type", Enum(InputType), nullable=False),
    Column("input_id", UUID(as_uuid=True), nullable=False),
    Column("result", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def start_mapper() -> None:
    registry_mapper.map_imperatively(
        User,
        user_account_table,
        properties={
            "_id": user_account_table.c.id,
            "_username": user_account_table.c.username,
            "_first_name": user_account_table.c.first_name,
            "_last_name": user_account_table.c.last_name,
            "_email": user_account_table.c.email,
            "_age": user_account_table.c.age,
            "_role": user_account_table.c.role,
            "_status": user_account_table.c.status,
            "_created_at": user_account_table.c.created_at,
            "_updated_at": user_account_table.c.updated_at,
        },
    )
    registry_mapper.map_imperatively(
        Task,
        task_record_table,
        properties={
            "_id": task_record_table.c.id,
            "_owner_id": task_record_table.c.owner_id,
            "_state": task_record_table.c.state,
            "_input_type": task_record_table.c.input_type,
            "_input_id": task_record_table.c.input_id,
            "_result": task_record_table.c.result,
            "_created_at": task_record_table.c.created_at,
            "_updated_at": task_record_table.c.updated_at,
        },
    )
    registry_mapper.map_imperatively(
        UserSession,
        user_session_table,
        properties={
            "_id": user_session_table.c.id,
            "_user_id": user_session_table.c.user_id,
            "_ip": user_session_table.c.ip,
            "_refresh_token": user_session_table.c.refresh_token,
            "_status": user_session_table.c.status,
            "_created_at": user_session_table.c.created_at,
            "_updated_at": user_session_table.c.updated_at,
        },
    )
    registry_mapper.map_imperatively(
        LocalAuthorization,
        local_authorization_table,
        properties={
            "_id": local_authorization_table.c.id,
            "_user_id": local_authorization_table.c.user_id,
            "_password": local_authorization_table.c.password,
            "_created_at": local_authorization_table.c.created_at,
            "_updated_at": local_authorization_table.c.updated_at,
        },
    )
    registry_mapper.map_imperatively(
        OAuthAuthorization,
        oauth_authorization_table,
        properties={
            "_id": oauth_authorization_table.c.id,
            "_user_id": oauth_authorization_table.c.user_id,
            "_created_at": oauth_authorization_table.c.created_at,
            "_updated_at": oauth_authorization_table.c.updated_at,
        },
    )
