from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UUID as SUUID
from sqlalchemy import DateTime
from sqlalchemy import Enum as SEnum
from sqlalchemy import Float, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class ProcessingStatus(str, Enum):
    """Статусы AI-обработки уведомления

    - PENDING - ожидание обработки
    - PROCESSNG - в обработке
    - COMPLETED - обработка завершена успешно
    - FAILED - обработка завершена с ошибкой
    """

    PENDING = "pending"
    PROCESSNG = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Notification(Base):
    """Схема таблицы уведомления"""

    __tablename__ = "notifications"
    id: Mapped[UUID] = mapped_column(
        SUUID(), primary_key=True, default=uuid4
    )  # Идентификатор уведомления
    user_id: Mapped[UUID] = mapped_column(
        SUUID(), nullable=False
    )  # Идентификатор пользователя
    title: Mapped[str] = mapped_column(
        String(length=50), nullable=False
    )  # Заголовок уведомления
    text: Mapped[str] = mapped_column(
        String(length=255), nullable=False
    )  # Текст уведомления
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )  # Дата и время создания уведомления
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )  # Дата и время прочтения уведомления

    # Результаты AI-анализа
    category: Mapped[str] = mapped_column(
        String(length=255), nullable=True
    )  # Категория уведомления
    confidence: Mapped[float] = mapped_column(
        Float, nullable=True
    )  # Оценка соответствия категории к тексту уведомления
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False
    )  # Статус обработки
