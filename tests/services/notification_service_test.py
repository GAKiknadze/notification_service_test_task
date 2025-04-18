from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import NotificationNotFoundExc
from src.models import Notification, ProcessingStatus
from src.services.notification_service import NotificationService


@pytest.mark.asyncio
async def test_create_notification():
    """Тест создания уведомления в базе данных"""
    mock_db = AsyncMock(spec=AsyncSession)

    user_id = uuid4()
    title = "Test Title"
    text = "Test Text"

    result = await NotificationService.create(mock_db, user_id, title, text)

    assert isinstance(result, Notification)
    assert result.user_id == user_id
    assert result.title == title
    assert result.text == text
    mock_db.add.assert_called_once_with(result)
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_notification_found():
    """Тест получения существующего уведомления из базы данных"""
    mock_db = AsyncMock(spec=AsyncSession)
    notification_id = uuid4()
    mock_notification = Notification(id=notification_id)
    mock_db.get = AsyncMock(return_value=mock_notification)

    result = await NotificationService.get(mock_db, notification_id)

    assert result == mock_notification
    mock_db.get.assert_awaited_once_with(Notification, notification_id)


@pytest.mark.asyncio
async def test_get_notification_not_found():
    """Тест получения несуществующего уведомления из базы данных"""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.get = AsyncMock(return_value=None)

    with pytest.raises(NotificationNotFoundExc):
        await NotificationService.get(mock_db, uuid4())


@pytest.mark.asyncio
async def test_mark_as_read():
    """Тест отметки уведомления как прочитанного"""
    mock_db = AsyncMock(spec=AsyncSession)
    notification_id = uuid4()
    mock_notification = Notification(id=notification_id)
    mock_db.get = AsyncMock(return_value=mock_notification)

    await NotificationService.mark_as_read(mock_db, notification_id)

    assert mock_notification.read_at is not None
    mock_db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_list_basic():
    """Тест получения базового списка уведомлений без фильтров"""
    mock_db = AsyncMock(spec=AsyncSession)
    mock_notifications = [Notification() for _ in range(3)]

    mock_count_result = AsyncMock()
    mock_count_result.scalar = MagicMock(return_value=3)

    mock_scalars_result = MagicMock()
    mock_scalars_result.all = MagicMock(return_value=mock_notifications)

    mock_result = AsyncMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars_result)

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

    notifications, total = await NotificationService.get_list(mock_db)

    assert len(notifications) == 3
    assert total == 3
    assert mock_db.execute.await_count == 2


@pytest.mark.asyncio
async def test_get_list_with_filters():
    """Тест получения списка уведомлений с применением всех фильтров"""
    mock_db = AsyncMock(spec=AsyncSession)
    user_id = uuid4()
    test_time = datetime.now()

    mock_count_result = AsyncMock()
    mock_count_result.scalar = MagicMock(return_value=1)

    mock_scalars_result = MagicMock()
    mock_scalars_result.all = MagicMock(return_value=[Notification()])

    mock_result = AsyncMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars_result)

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

    await NotificationService.get_list(
        db=mock_db,
        user_id=user_id,
        title="test",
        title_strict=False,
        text="search",
        created_at_start=test_time - timedelta(days=1),
        created_at_end=test_time,
        readed_at_start=test_time,
        category="news",
        confidence_start=0.5,
        processing_status=ProcessingStatus.COMPLETED,
        is_read=True,
        limit=5,
        offset=2,
    )

    assert mock_db.execute.await_count == 2

    select_call = mock_db.execute.call_args_list[1].args[0]
    query_str = str(select_call)

    assert "WHERE notifications.read_at IS NOT NULL" in query_str
    assert "notifications.user_id = :user_id_1" in query_str
    assert "lower(notifications.title) LIKE lower(:title_1)" in query_str
    assert "notifications.created_at >= :created_at_1" in query_str
    assert "notifications.created_at <= :created_at_2" in query_str
    assert "notifications.read_at >= :read_at_1" in query_str
    assert "lower(notifications.category) LIKE lower(:category_1)" in query_str
    assert "notifications.confidence >= :confidence_1" in query_str
    assert "notifications.processing_status = :processing_status_1" in query_str
    assert "LIMIT :param_1 OFFSET :param_2" in query_str
    mock_db.execute.assert_awaited()


@pytest.mark.asyncio
async def test_get_list_empty():
    """Тест получения пустого списка уведомлений"""
    mock_db = AsyncMock(spec=AsyncSession)

    mock_count_result = AsyncMock()
    mock_count_result.scalar = MagicMock(return_value=0)

    mock_scalars_result = MagicMock()
    mock_scalars_result.all = MagicMock(return_value=[])

    mock_result = AsyncMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars_result)

    mock_db.execute = AsyncMock(side_effect=[mock_count_result, mock_result])

    notifications, total = await NotificationService.get_list(mock_db)

    assert len(notifications) == 0
    assert total == 0
    assert mock_db.execute.await_count == 2
