from datetime import datetime
from typing import Any, Dict, Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import NotificationNotFoundExc
from ..logger import logger
from ..models import Notification, ProcessingStatus


class NotificationService:
    @staticmethod
    async def create(
        db: AsyncSession, user_id: UUID, title: str, text: str
    ) -> Notification:
        obj = Notification(user_id=user_id, title=title, text=text)
        await db.add(obj)  # type:ignore[func-returns-value]
        await db.commit()
        logger.bind(notification_id=obj.id, user_id=user_id, title=title).info(
            "Notification has been created"
        )
        return obj

    @staticmethod
    async def get(db: AsyncSession, _id: UUID) -> Notification:
        obj = await db.get(Notification, _id)
        if obj is None:
            logger.bind(notification_id=_id).warning("Notification not found")
            raise NotificationNotFoundExc
        logger.bind(notification_id=obj.id).info("Notification found")
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
        is_read: bool | None = None,
    ) -> Tuple[Sequence[Notification], int]:
        query = select(Notification)
        used_filters: Dict[str, Any] = dict()

        if is_read is not None:
            used_filters.update({"is_read": is_read})
            if is_read:
                query = query.where(Notification.read_at.isnot(None))
            else:
                query = query.where(Notification.read_at.is_(None))

        if user_id is not None:
            used_filters.update({"user_id": user_id})
            query = query.where(Notification.user_id == user_id)

        if title is not None:
            used_filters.update({"title": title, "title_strict": title_strict})
            if title_strict:
                query = query.where(Notification.title == title)
            else:
                query = query.where(Notification.title.ilike(f"%{title}%"))

        if text is not None:
            used_filters.update({"text": text})
            query = query.where(Notification.text.ilike(f"%{text}%"))

        if created_at_start is not None:
            used_filters.update({"created_at_start": created_at_start})
            query = query.where(Notification.created_at >= created_at_start)
        if created_at_end is not None:
            used_filters.update({"created_at_end": created_at_end})
            query = query.where(Notification.created_at <= created_at_end)

        if readed_at_start is not None:
            used_filters.update({"readed_at_start": readed_at_start})
            query = query.where(Notification.read_at >= readed_at_start)
        if readed_at_end is not None:
            used_filters.update({"readed_at_end": readed_at_end})
            query = query.where(Notification.read_at <= readed_at_end)

        if category is not None:
            used_filters.update(
                {"category": category, "category_strict": category_strict}
            )
            if category_strict:
                query = query.where(Notification.category == category)
            else:
                query = query.where(Notification.category.ilike(f"%{category}%"))

        if confidence_start is not None:
            used_filters.update({"confidence_start": confidence_start})
            query = query.where(Notification.confidence >= confidence_start)
        if confidence_end is not None:
            used_filters.update({"confidence_end": confidence_end})
            query = query.where(Notification.confidence <= confidence_end)

        if processing_status is not None:
            used_filters.update({"processing_status": processing_status})
            query = query.where(Notification.processing_status == processing_status)

        query = query.order_by(Notification.created_at.desc())

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        notifications = result.scalars().all()

        logger.bind(**used_filters).info(f"Notifications found: {total}")
        return (notifications, total)

    @staticmethod
    async def mark_as_read(db: AsyncSession, _id: UUID) -> None:
        obj = await NotificationService.get(db, _id)
        obj.read_at = func.now()
        await db.commit()
        logger.bind(notification_id=obj.id).info("The notification is marked as read")

    @staticmethod
    async def set_status(db: AsyncSession, _id: UUID, status: ProcessingStatus) -> None:
        obj = await NotificationService.get(db, _id)
        old_status = str(obj.processing_status)
        obj.processing_status = status
        await db.commit()
        logger.bind(notification_id=obj.id).info(
            f"Notification status changed from `{old_status}` to `{status}`"
        )

    @staticmethod
    async def add_ai_results(
        db: AsyncSession,
        _id: UUID,
        category: str | None = None,
        confidence: float | None = None,
    ) -> None:
        obj = await NotificationService.get(db, _id)
        if category is not None:
            obj.category = category
        if confidence is not None:
            obj.confidence = confidence
        obj.processing_status = ProcessingStatus.COMPLETED
        await db.commit()
        logger.bind(notification_id=obj.id).info(
            "AI evaluation results added to notification"
        )
