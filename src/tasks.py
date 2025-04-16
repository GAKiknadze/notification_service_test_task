from uuid import UUID

from celery import Celery, signals  # type:ignore[import-untyped]

from .config import Config
from .db import get_db, init_db
from .exceptions import NotificationNotFoundExc
from .models import ProcessingStatus
from .services.ai_service import AIService
from .services.notification_service import NotificationService

app = Celery("notification", broker=Config.broker.uri)


@signals.worker_init.connect
async def on_worker_start(sender, **kwargs):
    await init_db(Config.db.uri)


@app.task
async def notification_processing(notification_id: UUID) -> None:
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
