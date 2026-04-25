from prodik.application.errors import ApplicationError


class UserNotFoundError(ApplicationError): ...


class ModeratorCannotBeDeactivatedError(ApplicationError): ...
