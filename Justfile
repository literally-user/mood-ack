lint:
    ruff format
    ruff check --fix
    mypy . --strict

clean:
    docker compose -f docker-compose.base.yaml down -v

run target build="":
    #!/usr/bin/env bash
    BUILD_FLAG=""
    
    if [ "{{build}}" == "build" ]; then
        BUILD_FLAG="--build"
    fi

    if [ "{{target}}" == "prod" ]; then
        docker compose -f docker-compose.base.yaml -f docker-compose.prod.yaml up $BUILD_FLAG
    else
        docker compose -f docker-compose.base.yaml -f docker-compose.dev.yaml up $BUILD_FLAG
    fi