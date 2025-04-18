from typing import Literal

from pydantic import BaseModel, Field


class LoggerConfig(BaseModel):
    """Конфигурация логгирования"""

    level: Literal[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ] = Field(default="INFO")
