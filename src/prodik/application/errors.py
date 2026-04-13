from typing import Any, TypedDict


class ExceptionMeta(TypedDict):
    field: str
    value: Any


class ApplicationError(Exception):
    def __init__(self, detail: str, metadata: ExceptionMeta | None = None) -> None:
        self.detail = detail
        self.metadata = metadata
        super().__init__(detail)


class UserAlreadyExistsError(ApplicationError): ...


class UserNotFoundError(ApplicationError): ...


class InvalidCredentialsError(ApplicationError): ...


class UserDeactivatedError(ApplicationError): ...


class UserSessionExpiredError(ApplicationError): ...


class NotEnoughRightsError(ApplicationError): ...


class ModeratorCannotBeDeactivatedError(ApplicationError): ...


class ObjectFileNotFoundError(ApplicationError): ...


class UnsupportedFileExtensionError(ApplicationError): ...


class TaskNotFoundError(ApplicationError): ...
