from typing import Any, Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.errors import (
    AccessTokenExpiredError,
    ApplicationError,
    InvalidCredentialsError,
    ModeratorCannotBeDeactivatedError,
    NotEnoughRightsError,
    ObjectFileNotFoundError,
    TaskNotFoundError,
    UnsupportedFileExtensionError,
    UnsupportedProviderError,
    UserAlreadyExistsError,
    UserDeactivatedError,
    UserNotFoundError,
    UserSessionExpiredError,
    UserSessionRevokedError,
)
from prodik.domain.user.errors import DomainUserValidationError
from prodik.presentation.api.auth import router as auth_router
from prodik.presentation.api.root import router as root_router

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    UserAlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    UserDeactivatedError: status.HTTP_403_FORBIDDEN,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    UserSessionExpiredError: status.HTTP_401_UNAUTHORIZED,
    UserSessionRevokedError: status.HTTP_401_UNAUTHORIZED,
    AccessTokenExpiredError: status.HTTP_401_UNAUTHORIZED,
    NotEnoughRightsError: status.HTTP_403_FORBIDDEN,
    ModeratorCannotBeDeactivatedError: status.HTTP_409_CONFLICT,
    ObjectFileNotFoundError: status.HTTP_404_NOT_FOUND,
    UnsupportedFileExtensionError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    TaskNotFoundError: status.HTTP_404_NOT_FOUND,
    UnsupportedProviderError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    DomainUserValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


def _resolve_status_code(exception: ApplicationError) -> int:
    for exception_type in type(exception).mro():
        if not issubclass(exception_type, ApplicationError):
            continue

        status_code = EXCEPTION_HANDLERS.get(exception_type)
        if status_code is not None:
            return status_code

    return status.HTTP_500_INTERNAL_SERVER_ERROR


async def application_error_handler(
    _request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = _resolve_status_code(exception)

    response_body: dict[str, Any] = {
        "detail": exception.detail,
    }

    if exception.metadata:
        response_body["meta"] = exception.metadata

    return JSONResponse(status_code=status_code, content=response_body)


def include_handlers(app: FastAPI) -> None:
    app.include_router(root_router)
    app.include_router(auth_router)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
