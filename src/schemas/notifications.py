from datetime import datetime
from typing import Any, Dict, Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ..models import ProcessingStatus


class NotificationCreate(BaseModel):
    """Тело запроса на создание уведомления"""

    user_id: UUID = Field(..., description="Идентификатор пользователя")
    title: str = Field(max_length=50, description="Заголовок уведомления")
    text: str = Field(max_length=255, description="Текст уведомления")


class Notification(BaseModel):
    """Объект уведомления"""

    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field(..., description="Идентификатор уведомления")
    user_id: UUID = Field(..., description="Идентификатор пользователя")
    title: str = Field(..., description="Заголовок уведомления")
    text: str = Field(..., description="Текст уведомления")
    created_at: datetime = Field(..., description="Дата и время создания уведомления")
    read_at: datetime | None = Field(
        default=None, description="Дата и время прочтения уведомления"
    )
    category: str | None = Field(default=None, description="Категория уведомления")
    confidence: float | None = Field(
        default=None, description="Оценка соответствия контента категории уведомления"
    )
    processing_status: ProcessingStatus = Field(
        ..., description="Статус обработки уведомления"
    )


class NotificationFilters(BaseModel):
    """Фильтры для поиска по уведомлений"""

    user_id: UUID | None = Field(default=None, description="Идентификатор пользователя")
    title: str | None = Field(default=None, description="Заголовок уведомления")
    title_strict: bool = Field(
        default=True,
        description="Если True поиск полного соответствия, иначе поиск подстроки",
    )
    text: str | None = Field(default=None, description="Текст уведомления")
    created_at_start: datetime | None = Field(
        default=None, description="Время и дата начала создания уведомления"
    )
    created_at_end: datetime | None = Field(
        default=None, description="Время и дата завершения создания уведомления"
    )
    readed_at_start: datetime | None = Field(
        default=None, description="Время и дата начала прочтения уведомления"
    )
    readed_at_end: datetime | None = Field(
        default=None, description="Время и дата завершения прочтения уведомления"
    )
    category: str | None = Field(default=None, description="Категория уведомления")
    category_strict: bool = Field(
        default=False,
        description="Если True поиск полного соответствия, иначе поиск подстроки",
    )
    confidence_start: float | None = Field(
        default=None,
        description="Нижний порог оценки соответствия контента категории уведомления",
    )
    confidence_end: float | None = Field(
        default=None,
        description="Верхний порог оценки соответствия контента категории уведомления",
    )
    processing_status: ProcessingStatus | None = Field(
        default=None, description="Статус обработки уведомления"
    )
    limit: int = Field(default=10, description="Лимит записей в запросе")
    offset: int = Field(default=0, description="Смещение по записям")
    is_read: bool | None = Field(
        default=None, description="Отобразить только прочтенные уведомления"
    )

    @staticmethod
    def validate_range(values: Any, start: str, end: str) -> Any:
        if isinstance(values, Dict):
            start_value = values.get(start)
            end_value = values.get(end)
            if start_value is not None and end_value is not None:
                if start_value > end_value:
                    raise ValueError(f"`{start}` cannot be greater than `{end}`")
        return values

    @model_validator(mode="before")
    @classmethod
    def validate_created_at_range(cls, values: Any) -> Any:
        return cls.validate_range(values, "created_at_start", "created_at_end")

    @model_validator(mode="before")
    @classmethod
    def validate_readed_at_range(cls, values: Any) -> Any:
        return cls.validate_range(values, "readed_at_start", "readed_at_end")

    @model_validator(mode="before")
    @classmethod
    def validate_confidence_range(cls, values: Any) -> Any:
        return cls.validate_range(values, "confidence_start", "confidence_end")


class NotificationsList(BaseModel):
    """Тело ответа список уведомлений"""

    model_config = ConfigDict(from_attributes=True)
    data: Sequence[Notification] = Field(
        default=[], description="Список найденных уведомлений"
    )
    count: int = Field(default=0, description="Количество найденных записей")
    limit: int = Field(..., description="Лимит записей")
    offset: int = Field(..., description="Смещение по записям")


class NotificationStatus(BaseModel):
    """Статус уведомления"""

    status: ProcessingStatus = Field(..., description="Статус обработки уведомления")
