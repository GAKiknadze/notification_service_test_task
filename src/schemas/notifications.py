from datetime import datetime
from typing import Sequence
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from ..models import ProcessingStatus


class NotificationCreate(BaseModel):
    user_id: UUID = Field()
    title: str = Field(max_length=50)
    text: str = Field(max_length=255)


class Notification(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID = Field()
    user_id: UUID = Field()
    title: str = Field()
    text: str = Field()
    created_at: datetime = Field()
    read_at: datetime | None = Field(default=None)
    category: str | None = Field(default=None)
    confidence: float | None = Field(default=None)
    processing_status: ProcessingStatus = Field()


class NotificationFilters(BaseModel):
    user_id: UUID | None = Field(default=None)
    title: str | None = Field(default=None)
    title_strict: bool = Field(default=True)
    text: str | None = Field(default=None)
    created_at_start: datetime | None = Field(default=None)
    created_at_end: datetime | None = Field(default=None)
    readed_at_start: datetime | None = Field(default=None)
    readed_at_end: datetime | None = Field(default=None)
    category: str | None = Field(default=None)
    category_strict: bool = Field(default=False)
    confidence_start: float | None = Field(default=None)
    confidence_end: float | None = Field(default=None)
    processing_status: ProcessingStatus | None = Field(default=None)
    limit: int = Field(default=10)
    offset: int = Field(default=0)
    is_read: bool | None = Field(default=None)


class NotificationsList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    data: Sequence[Notification] = Field(default=[])
    count: int = Field(default=0)
    limit: int = Field()
    offset: int = Field()


class NotificationStatus(BaseModel):
    status: ProcessingStatus = Field()
