import logging
import sys

from loguru import logger

from .config import Config


class InterceptHandler(logging.Handler):
    """Обертка Loguru-логгера"""

    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def setup_logger():
    """Инициализация Loguru-логгера и заглушка встроенных логгеров"""
    logging.getLogger().handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("fastapi").handlers = []
    logging.getLogger("uvicorn.error").handlers = []
    logging.getLogger("uvicorn.error").propagate = False

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False

    logging.getLogger("uvicorn.asgi").handlers = []
    logging.getLogger("uvicorn.asgi").propagate = True

    logger.add(
        sink=sys.stdout,
        level=Config.logger.level,
        enqueue=True,
        # serialize=True,
    )


setup_logger()

__all__ = ["logger"]
