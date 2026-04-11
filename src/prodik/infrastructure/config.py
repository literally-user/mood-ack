import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True, kw_only=True)
class APIConfig:
    host: str
    port: int
    persistence: str

    debug: bool
    secret: str


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    api: APIConfig


def load_config() -> Config:
    config_path = Path("config.toml")  # объект Path
    with config_path.open("rb") as file:
        config = tomllib.load(file)
        return Config(
            api=APIConfig(
                host=config["api"]["host"],
                port=config["api"]["port"],
                persistence=config["api"]["persistence"],
                debug=os.getenv("DEBUG", "false") in ("true", "false"),
                secret=config["api"]["secret"],
            )
        )
