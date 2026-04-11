from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from prodik.bootstrap.di import get_async_container
from prodik.bootstrap.logs import configure_structlog
from prodik.infrastructure.config import Config, load_config
from prodik.presentation.common import (
    include_exception_handlers,
    include_handlers,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app(config: Config) -> FastAPI:
    app = FastAPI(
        lifespan=lifespan,
        docs_url="/docs" if config.api.debug else None,
        redoc_url="/redoc" if config.api.debug else None,
        openapi_url="/openapi.json" if config.api.debug else None,
        title="application",
        description="Great & powerful application",
        version="0.1.0",
    )

    include_handlers(app)
    include_exception_handlers(app)

    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


def run_http(_argv: list[str]) -> None:
    config = load_config()

    app = create_app(config)
    container = get_async_container(config)
    log_configuration = configure_structlog()

    setup_dishka(app=app, container=container)

    uvicorn.run(
        app=app,
        host=config.api.host,
        port=config.api.port,
        log_config=log_configuration,
    )
