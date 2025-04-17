from fastapi import Request, status
from fastapi.responses import JSONResponse

from .exceptions import NotificationNotFoundExc
from .logger import logger


async def handle_notification_not_found(
    req: Request, exc: NotificationNotFoundExc
) -> JSONResponse:
    """Обработчик исключения `NotificationNotFoundExc`

    Аргументы:
        req (Request): Объект запроса
        exc (NotificationNotFoundExc): Объект вызванного исключения

    Возвращает:
        JSONResponse: Краткое описание ошибки
    """
    return JSONResponse(
        content={"msg": "Notification not found"}, status_code=status.HTTP_404_NOT_FOUND
    )


async def handle_any_exception(req: Request, exc: Exception) -> JSONResponse:
    """Обработчик всех возникших исключений, не учтенных в других обработчиках

    Аргументы:
        req (Request): Объект запроса
        exc (Exception): Объект вызванного исключения

    Возвращает:
        JSONResponse: Краткое описание ошибки
    """
    request_details = {
        "url": str(req.url),
        "method": req.method,
        "headers": dict(req.headers),
        "query_params": dict(req.query_params),
        "path_params": req.path_params,
    }

    logger.opt(exception=exc).error(
        "Unhandled exception occurred",
        request=request_details,
        error_type=type(exc).__name__,
        error_message=str(exc),
    )
    return JSONResponse(
        content={"msg": "Something wrong"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
