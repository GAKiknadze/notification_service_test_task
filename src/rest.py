from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import Config
from .db import init_db
from .exceptions import NotificationNotFoundExc
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
    await init_db(Config.db.uri)


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
    return JSONResponse(
        content={"msg": "Something wrong"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
