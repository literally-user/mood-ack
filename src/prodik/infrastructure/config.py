import os
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True, frozen=True, kw_only=True)
class APIConfig:
    host: str
    port: int

    debug: bool
    secret: str
    expires_in: int


@dataclass(slots=True, frozen=True, kw_only=True)
class PersistenceConfig:
    url: str


@dataclass(slots=True, frozen=True, kw_only=True)
class ObjectStorageConfig:
    bucket: str
    access_key: str
    secret_key: str
    region: str
    url: str


@dataclass(slots=True, frozen=True, kw_only=True)
class Config:
    api: APIConfig
    persistence: PersistenceConfig
    object_storage: ObjectStorageConfig


def load_config() -> Config:
    config_path = Path("config.toml")  # объект Path
    with config_path.open("rb") as file:
        config = tomllib.load(file)
        return Config(
            api=APIConfig(
                host=config["api"]["host"],
                port=config["api"]["port"],
                expires_in=config["api"]["expires_in"],
                debug=os.getenv("DEBUG", "false") in ("true", "false"),
                secret=config["api"]["secret"],
            ),
            persistence=PersistenceConfig(
                url=config["api"]["persistence"],
            ),
            object_storage=ObjectStorageConfig(
                bucket=config["object_storage"]["bucket"],
                access_key=config["object_storage"]["access_key"],
                secret_key=config["object_storage"]["secret_key"],
                region=config["object_storage"]["region"],
                url=config["object_storage"]["url"],
            ),
        )
