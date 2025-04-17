from pydantic import BaseModel, Field


class BrokerConfig(BaseModel):
    """Конфигурация брокера сообщений для Celery"""

    uri: str = Field(..., alias="uri")
