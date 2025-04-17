from typing import List

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Конфигурация сервера"""

    cors: List[str] = Field(default_factory=lambda: ["*"])
