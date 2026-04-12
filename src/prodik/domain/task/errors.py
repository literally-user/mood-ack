from prodik.application.errors import ApplicationError


class TaskResultGreaterThanError(ApplicationError): ...


class TaskResultLessThanError(ApplicationError): ...


class CannotDeprecateFinishedTaskError(ApplicationError): ...
