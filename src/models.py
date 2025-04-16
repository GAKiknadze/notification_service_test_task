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
    PENDING = "pending"
    PROCESSNG = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[UUID] = mapped_column(SUUID(), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(SUUID(), nullable=False)
    title: Mapped[str] = mapped_column(String(length=50), nullable=False)
    text: Mapped[str] = mapped_column(String(length=255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Результаты AI-анализа
    category: Mapped[str] = mapped_column(String(length=255), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        SEnum(ProcessingStatus), default=ProcessingStatus.PENDING, nullable=False
    )
