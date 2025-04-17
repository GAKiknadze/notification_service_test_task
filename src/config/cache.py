from typing import Dict

from pydantic import BaseModel, Field


class CacheConfig(BaseModel):
    """Конфигурация кэша"""

    uri: str | None = Field(default=None)
    ttls: Dict[str, int] = Field(default={})
    max_content_size: int = Field(default=0)
