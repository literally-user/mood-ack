import argparse
import contextlib
from collections.abc import Iterator
from importlib.resources import as_file, files
from pathlib import Path

import alembic.config

import prodik.infrastructure.persistence
from prodik.bootstrap.api import run_http
from prodik.infrastructure.persistence import start_mapper


def get_alembic_config_path() -> Iterator[Path]:
    source = files(prodik.infrastructure.persistence).joinpath("alembic.ini")
    with as_file(source) as path:
        yield path


def run_migrations(*_args: str) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(
        argv=["-c", alembic_path, "upgrade", "head"],
    )
    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


def autogenerate_migrations(*args: str) -> None:
    alembic_path_gen = get_alembic_config_path()
    alembic_path = str(next(alembic_path_gen))
    alembic.config.main(
        argv=["-c", alembic_path, "revision", "--autogenerate", "-m", args[0]],
    )

    with contextlib.suppress(StopIteration):
        next(alembic_path_gen)


def configure_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Anti-Frodik",
        description="Anti-frod application",
    )

    subparsers = parser.add_subparsers(dest="module", required=True)

    api_parser = subparsers.add_parser("api", help="API service")
    api_sub = api_parser.add_subparsers(dest="option", required=True)

    api_run = api_sub.add_parser("run", help="Run API")
    api_run.set_defaults(func=run_http)

    mig_parser = subparsers.add_parser("migrations", help="Database migrations")
    mig_sub = mig_parser.add_subparsers(dest="option", required=True)

    mig_upgrade = mig_sub.add_parser("upgrade", help="Apply migrations")
    mig_upgrade.set_defaults(func=run_migrations)

    mig_generate = mig_sub.add_parser("generate", help="Generate migration")
    mig_generate.add_argument("message", type=str)
    mig_generate.set_defaults(func=lambda args: autogenerate_migrations(args.message))

    return parser


def main() -> None:
    parser = configure_argument_parser()
    args = parser.parse_args()

    if args.module == "api":
        run_migrations()

    start_mapper()

    args.func(args)
