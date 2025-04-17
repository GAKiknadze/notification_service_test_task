import uuid

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Config
from .db import init_db
from .exceptions import NotificationNotFoundExc
from .logger import logger
from .routes import notifications

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=Config.server.cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    logger.info("Initializing database")
    await init_db(Config.db.uri)
    logger.info("Server started on http://localhost:8000")


@app.middleware("http")
async def log_requests(request: Request, call_next):
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


app.include_router(notifications.router, prefix="/notifications")


@app.exception_handler(NotificationNotFoundExc)
async def handle_notification_not_found(
    req: Request, exc: NotificationNotFoundExc
) -> JSONResponse:
    return JSONResponse(
        content={"msg": "Notification not found"}, status_code=status.HTTP_404_NOT_FOUND
    )


@app.exception_handler(Exception)
async def handle_any_exception(req: Request, exc: Exception) -> JSONResponse:
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
