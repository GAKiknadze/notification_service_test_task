from datetime import datetime
from typing import Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import NotificationNotFoundExc
from ..models import Notification, ProcessingStatus


class NotificationService:
    @staticmethod
    async def create(
        db: AsyncSession, user_id: UUID, title: str, text: str
    ) -> Notification:
        obj = Notification(user_id=user_id, title=title, text=text)
        await db.add(obj)  # type:ignore[func-returns-value]
        return obj

    @staticmethod
    async def get(db: AsyncSession, _id: UUID) -> Notification:
        obj = await db.get(Notification, _id)
        if obj is None:
            raise NotificationNotFoundExc
        return obj

    @staticmethod
    async def get_list(
        db: AsyncSession,
        user_id: UUID | None = None,
        title: str | None = None,
        title_strict: bool = True,
        text: str | None = None,
        created_at_start: datetime | None = None,
        created_at_end: datetime | None = None,
        readed_at_start: datetime | None = None,
        readed_at_end: datetime | None = None,
        category: str | None = None,
        category_strict: bool = False,
        confidence_start: float | None = None,
        confidence_end: float | None = None,
        processing_status: ProcessingStatus | None = None,
        limit: int = 10,
        offset: int = 0,
        is_read: bool = False,
    ) -> Tuple[Sequence[Notification], int]:
        query = select(Notification)

        if is_read:
            query = query.where(Notification.read_at.isnot(None))
        else:
            query = query.where(Notification.read_at.is_(None))

        if user_id is not None:
            query = query.where(Notification.user_id == user_id)

        if title is not None:
            if title_strict:
                query = query.where(Notification.title == title)
            else:
                query = query.where(Notification.title.ilike(f"%{title}%"))

        if text is not None:
            query = query.where(Notification.text.ilike(f"%{text}%"))

        if created_at_start is not None:
            query = query.where(Notification.created_at >= created_at_start)
        if created_at_end is not None:
            query = query.where(Notification.created_at <= created_at_end)

        if readed_at_start is not None:
            query = query.where(Notification.read_at >= readed_at_start)
        if readed_at_end is not None:
            query = query.where(Notification.read_at <= readed_at_end)

        if category is not None:
            if category_strict:
                query = query.where(Notification.category == category)
            else:
                query = query.where(Notification.category.ilike(f"%{category}%"))

        if confidence_start is not None:
            query = query.where(Notification.confidence >= confidence_start)
        if confidence_end is not None:
            query = query.where(Notification.confidence <= confidence_end)

        if processing_status is not None:
            query = query.where(Notification.processing_status == processing_status)

        query = query.order_by(Notification.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        notifications = result.scalars().all()

        return (notifications, total)

    @staticmethod
    async def check_as_read(db: AsyncSession, _id: UUID) -> None:
        obj = await NotificationService.get(db, _id)
        obj.read_at = func.now()
        await db.commit()
