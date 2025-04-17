from pydantic import BaseModel, Field


class DBConfig(BaseModel):
    """Конфигурация базы данных"""

    uri: str = Field(..., alias="uri")
