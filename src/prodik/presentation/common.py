from typing import Final

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from prodik.application.errors import ApplicationError, UserAlreadyExistsError

EXCEPTION_HANDLERS: Final[dict[type[ApplicationError], int]] = {
    UserAlreadyExistsError: status.HTTP_400_BAD_REQUEST
}


async def application_error_handler(
    _request: Request, exception: ApplicationError
) -> JSONResponse:
    status_code = EXCEPTION_HANDLERS.get(
        type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    return JSONResponse(status_code=status_code, content=exception.detail)


def include_handlers(app: FastAPI) -> None:
    # app.include_router(your_router)
    pass


def include_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApplicationError, application_error_handler)  # type: ignore
