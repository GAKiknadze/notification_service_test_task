import traceback
from uuid import UUID

from asgiref.sync import async_to_sync
from celery import Celery, signals  # type:ignore[import-untyped]

from .config import Config
from .db import get_db, init_db
from .exceptions import NotificationNotFoundExc
from .logger import logger
from .models import ProcessingStatus
from .services.ai_service import AIService
from .services.notification_service import NotificationService

app = Celery("notification", broker=Config.broker.uri)


@signals.worker_process_init.connect
def on_start(*args, **kwargs):
    async_to_sync(init_db)(Config.db.uri)


async def calculate(notification_id: UUID) -> None:
    logger.bind(notification_id=notification_id).debug("Start of processing")
    async with get_db() as db:
        try:
            await NotificationService.set_status(
                db, notification_id, ProcessingStatus.PROCESSNG
            )
            obj = await NotificationService.get(db, notification_id)
            result = await AIService.analyze_text(obj.text)
            await NotificationService.add_ai_results(
                db,
                notification_id,
                category=result.get("category"),
                confidence=result.get("confidence"),
            )
        except NotificationNotFoundExc:
            pass
        except Exception:
            await NotificationService.set_status(
                db, notification_id, ProcessingStatus.FAILED
            )
            logger.bind(notification_id=notification_id).critical(
                traceback.format_exc()
            )
    logger.bind(notification_id=notification_id).debug("End of processing")


@app.task
def notification_processing(notification_id: UUID) -> None:
    async_to_sync(calculate)(notification_id)
