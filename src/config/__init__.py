from typing import Tuple, Type

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from .broker import BrokerConfig
from .cache import CacheConfig
from .db import DBConfig
from .logger import LoggerConfig
from .server import ServerConfig


class _Config(BaseSettings):
    """Корневой класс конфигурации"""

    model_config = SettingsConfigDict(
        yaml_file="config.yaml",
        yaml_file_encoding="utf-8",
        extra="ignore",
    )

    db: DBConfig
    cache: CacheConfig
    broker: BrokerConfig
    server: ServerConfig
    logger: LoggerConfig

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


Config = _Config()  # type:ignore[call-arg]

__all__ = ["Config"]
