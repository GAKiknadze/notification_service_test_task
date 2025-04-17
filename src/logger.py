import logging

from loguru import logger

from .config import Config


class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


def setup_logger():
    logging.getLogger().handlers = [InterceptHandler()]
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("fastapi").handlers = []

    logger.add(
        sink=Config.logger.path,
        rotation=Config.logger.rotation,
        level=Config.logger.level,
        enqueue=True,
        serialize=True,
    )


setup_logger()

__all__ = ["logger"]
