from typing import Any, Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.auth.errors import (
    AccessTokenExpiredError,
    InvalidCredentialsError,
    UserDeactivatedError,
    UserSessionRevokedError,
)
from prodik.application.content_processing.errors import (
    ObjectFileNotFoundError,
    UnsupportedFileExtensionError,
)
from prodik.application.errors import ApplicationError
from prodik.application.manage_task.errors import TaskNotFoundError
from prodik.application.manage_user.errors import (
    ModeratorCannotBeDeactivatedError,
    UserNotFoundError,
)
from prodik.domain.user.errors import DomainUserValidationError, NotEnoughRightsError
from prodik.presentation.api.auth import router as auth_router
from prodik.presentation.api.file import router as file_router
from prodik.presentation.api.model import router as model_router
from prodik.presentation.api.root import router as root_router
from prodik.presentation.api.task import router as task_router
from prodik.presentation.api.user import router as user_router

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    ObjectFileNotFoundError: status.HTTP_404_NOT_FOUND,
    UnsupportedFileExtensionError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    UserNotFoundError: status.HTTP_404_NOT_FOUND,
    TaskNotFoundError: status.HTTP_404_NOT_FOUND,
    UserDeactivatedError: status.HTTP_403_FORBIDDEN,
    NotEnoughRightsError: status.HTTP_403_FORBIDDEN,
    UserSessionRevokedError: status.HTTP_403_FORBIDDEN,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
    AccessTokenExpiredError: status.HTTP_401_UNAUTHORIZED,
    ModeratorCannotBeDeactivatedError: status.HTTP_409_CONFLICT,
    DomainUserValidationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


async def application_error_handler(
    _request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = None
    exceptions = EXCEPTION_HANDLERS.keys()
    for i in type(exception).mro():
        if i in exceptions:
            status_code = EXCEPTION_HANDLERS[i]
    if status_code is None:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    response_body: dict[str, Any] = {
        "detail": exception.detail,
    }

    if exception.metadata:
        response_body["meta"] = exception.metadata

    return JSONResponse(status_code=status_code, content=response_body)


def include_handlers(app: FastAPI) -> None:
    app.include_router(model_router)
    app.include_router(root_router)
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(task_router)
    app.include_router(file_router)


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
