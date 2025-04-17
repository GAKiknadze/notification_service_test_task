from datetime import datetime
from typing import Any, Dict, Sequence, Tuple
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..exceptions import NotificationNotFoundExc
from ..logger import logger
from ..models import Notification, ProcessingStatus


class NotificationService:
    """Класс для работы с уведомлениями в базе данных"""

    @staticmethod
    async def create(
        db: AsyncSession, user_id: UUID, title: str, text: str
    ) -> Notification:
        """Записать уведомление в базу данных

        Аргументы:
            db (AsyncSession): Активная сессия базы данных
            user_id (UUID): Идентификатор пользователя
            title (str): Заголовок уведомления
            text (str): Тело уведомления

        Возвращает:
            Notification: Объект уведомления
        """
        obj = Notification(user_id=user_id, title=title, text=text)
        db.add(obj)
        await db.commit()
        logger.bind(notification_id=obj.id, user_id=user_id, title=title).info(
            "Notification has been created"
        )
        return obj

    @staticmethod
    async def get(db: AsyncSession, _id: UUID) -> Notification:
        """Получить уведомление из базы данных

        Аргументы:
            db (AsyncSession): Активная сессия базы данных
            _id (UUID): Идентификатор уведомления

        Вызывает исключения:
            NotificationNotFoundExc: Если уведомление с идентификатором не найдено

        Возвращает:
            Notification: Объект уведомления
        """
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
        """Получить список уведомлений на основе фильтров

        Аргументы:
            db (AsyncSession): Активная сессия базы данных
            user_id (UUID | None, optional): Идентификатор пользователя. По умолчанию `None`.
            title (str | None, optional): Заголовок уведомления. По умолчанию `None`.
            title_strict (bool, optional): Если True поиск полного соответствия, иначе поиск подстроки. По умолчанию `True`.
            text (str | None, optional): Текст уведомления. По умолчанию `None`.
            created_at_start (datetime | None, optional): Время и дата начала создания уведомления. По умолчанию `None`.
            created_at_end (datetime | None, optional): Время и дата завершения создания уведомления. По умолчанию `None`.
            readed_at_start (datetime | None, optional): Время и дата начала прочтения уведомления. По умолчанию `None`.
            readed_at_end (datetime | None, optional): Время и дата завершения прочтения уведомления. По умолчанию `None`.
            category (str | None, optional): Категория уведомления. По умолчанию `None`.
            category_strict (bool, optional): Если True поиск полного соответствия, иначе поиск подстроки.
            По умолчанию `False`.
            confidence_start (float | None, optional): Нижний порог оценки соответствия контента категории уведомления.
            По умолчанию `None`.
            confidence_end (float | None, optional): Верхний порог оценки соответствия контента категории уведомления.
            По умолчанию `None`.
            processing_status (ProcessingStatus | None, optional): Статус обработки уведомления. По умолчанию `None`.
            limit (int, optional): Лимит записей в запросе. По умолчанию `10`.
            offset (int, optional): Смещение по записям. По умолчанию `0`.
            is_read (bool | None, optional): Отобразить только прочтенные уведомления. По умолчанию `None`.

        Возвращает:
            Tuple[Sequence[Notification], int]: Последовательность найденных уведомлений и общее количество найденных по
            фильтрам записей
        """
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
        """Пометить уведомление прочитанным

        Аргументы:
            db (AsyncSession): Активная сессия базы данных
            _id (UUID): Идентификатор уведомления

        Вызывает исключения:
            NotificationNotFoundExc: Если уведомление с идентификатором не найдено
        """
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
        """Добавить результаты AI-обработки

        Аргументы:
            db (AsyncSession): Активная сессия базы данных
            _id (UUID): Идентификатор уведомления
            category (str | None, optional): Категория уведомления. По умолчанию `None`.
            confidence (float | None, optional): Оценка соответствия категории к тексту уведомления. По умолчанию `None`.

        Вызывает исключения:
            NotificationNotFoundExc: Если уведомление с идентификатором не найдено
        """
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
