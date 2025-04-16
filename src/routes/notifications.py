from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.notifications import (
    Notification,
    NotificationCreate,
    NotificationFilters,
    NotificationsList,
    NotificationStatus,
)
from ..services.notification_service import NotificationService
from ..tasks import notification_processing

router = APIRouter()


@router.post("/", response_model=Notification, status_code=status.HTTP_201_CREATED)
async def create_notification(
    data: Annotated[NotificationCreate, Body(embed=True)],
    db: AsyncSession = Depends(get_db),
) -> Notification:
    obj = await NotificationService.create(db, **data.model_dump())
    notification_processing.delay(obj.id)
    return Notification.model_validate(obj)


@router.get("/", response_model=NotificationsList, status_code=status.HTTP_200_OK)
async def get_notifications_list(
    filters: Annotated[NotificationFilters, Query()], db: AsyncSession = Depends(get_db)
) -> NotificationsList:
    objects, count = await NotificationService.get_list(db, **filters.model_dump())
    return NotificationsList(
        data=objects,  # type:ignore[arg-type]
        count=count,
        limit=filters.limit,
        offset=filters.offset,
    )


@router.get(
    "/{notification_id}", response_model=Notification, status_code=status.HTTP_200_OK
)
async def get_notification_by_id(
    notification_id: UUID, db: AsyncSession = Depends(get_db)
) -> Notification:
    obj = await NotificationService.get(db, notification_id)
    return Notification.model_validate(obj)


@router.get(
    "/{notification_id}/status",
    response_model=NotificationStatus,
    status_code=status.HTTP_200_OK,
)
async def get_notification_status_by_id(
    notification_id: UUID, db: AsyncSession = Depends(get_db)
) -> NotificationStatus:
    obj = await NotificationService.get(db, notification_id)
    return NotificationStatus(status=obj.processing_status)


@router.post(
    "/{notification_id}/read",
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_notification_as_read(
    notification_id: UUID, db: AsyncSession = Depends(get_db)
) -> Response:
    await NotificationService.mark_as_read(db, notification_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
