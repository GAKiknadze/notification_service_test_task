from typing import Literal

from pydantic import BaseModel, Field


class LoggerConfig(BaseModel):
    path: str = Field(default="logs/app.json")
    rotation: str = Field(default="10 MB")
    level: Literal[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ] = Field(default="INFO")
