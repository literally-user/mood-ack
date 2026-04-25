from prodik.application.errors import ApplicationError


class ObjectFileNotFoundError(ApplicationError): ...


class UnsupportedFileExtensionError(ApplicationError): ...


class TaskAlreadyExistsError(ApplicationError): ...
