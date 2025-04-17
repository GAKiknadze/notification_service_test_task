import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from .config import Config
from .db import create_tables, init_engine
from .exception_handlers import handle_any_exception, handle_notification_not_found
from .exceptions import NotificationNotFoundExc
from .logger import logger
from .v1.routes import notifications

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    """Функция подготовки перед запуском FastApi-сервера"""
    logger.info("Initializing database")
    await init_engine(Config.db.uri)
    await create_tables()
    logger.info("Server started on http://localhost:8000")


# Объявление CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.server.cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Промежуточный слой, отвечающий за логирование обработки запросов.

    - Генерирует уникальный идентификатор запроса
    - Вставляет в дочерние логи идентификатор запроса
    - Сигнализирует в логах о возникших ошибках

    Аргументы:
        request (Request): Объект запроса
        call_next (Callable[[Any], Any]): Callable-объект для дальнейшей обработки запроса

    Возвращает:
        Response: Ответ запроса или исключение
    """
    request_id = str(uuid.uuid4())
    with logger.contextualize(request_id=request_id):
        logger.info(f"Request: {request.method} {request.url}")
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.success(f"Response: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            raise
        finally:
            logger.debug("Request finished")


# Подключение роутера уведомлений
app.include_router(notifications.router, prefix="/v1/notifications")

# Подключение обработчиков исключений
app.add_exception_handler(
    NotificationNotFoundExc, handle_notification_not_found  # type:ignore[arg-type]
)
app.add_exception_handler(Exception, handle_any_exception)
