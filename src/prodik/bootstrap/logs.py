from typing import Any, Final

import structlog

type LoggingConfiguration = dict[str, Any]


def configure_structlog() -> LoggingConfiguration:
    processors: Final[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.dict_tracebacks,
        structlog.processors.UnicodeDecoder(),
    ]

    structlog.configure(
        processors=[
            *processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    json_formatter: dict[str, Any] = {
        "()": structlog.stdlib.ProcessorFormatter,
        "processor": structlog.processors.JSONRenderer(
            sort_keys=True,
            ensure_ascii=False,
        ),
        "foreign_pre_chain": processors,
    }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": json_formatter,
        },
        "handlers": {
            "json": {
                "class": "logging.StreamHandler",
                "formatter": "json",
                "stream": "ext://sys.stdout",
            },
        },
        "root": {
            "level": "DEBUG",
            "handlers": ["json"],
        },
        "loggers": {
            "uvicorn": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "CRITICAL",
                "handlers": ["json"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["json"],
                "propagate": False,
            },
        },
    }
