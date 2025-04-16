from pydantic_settings import BaseSettings, SettingsConfigDict

from .broker import BrokerConfig
from .db import DBConfig
from .server import ServerConfig


class _Config(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="config.yml",
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    db: DBConfig
    broker: BrokerConfig
    server: ServerConfig


Config = _Config()  # type:ignore[call-arg]
