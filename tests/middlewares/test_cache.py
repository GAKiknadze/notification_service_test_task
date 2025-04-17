from unittest.mock import AsyncMock

import pytest
from aiocache import Cache  # type:ignore[import-untyped]
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middlewares.cache import CacheMiddleware


@pytest.fixture
def test_app():
    """Фикстура для создания тестового приложения с CacheMiddleware"""

    def _test_app(cached_endpoints):
        app = FastAPI()
        cache = Cache(Cache.MEMORY)
        app.add_middleware(
            CacheMiddleware, cache=cache, cached_endpoints=cached_endpoints
        )
        return app

    return _test_app


def test_cached_response(test_app):
    """GET-запросы к кэшируемым эндпоинтам возвращают закэшированный ответ"""
    cached_endpoints = {"/cached": 60}
    app = test_app(cached_endpoints)
    call_count = 0

    @app.get("/cached")
    async def get_cached():
        nonlocal call_count
        call_count += 1
        return {"count": call_count}

    client = TestClient(app)

    response1 = client.get("/cached")
    assert response1.json() == {"count": 1}

    response2 = client.get("/cached")
    assert response2.json() == {"count": 1}


def test_query_params_cache_key(test_app):
    """Разные query-параметры создают разные ключи кэша"""
    cached_endpoints = {"/cached": 60}
    app = test_app(cached_endpoints)
    call_count = 0

    @app.get("/cached")
    async def get_cached(param: int | None = None):
        nonlocal call_count
        call_count += 1
        return {"count": call_count, "param": param}

    client = TestClient(app)

    client.get("/cached?param=1")
    response = client.get("/cached?param=1")
    assert response.json()["count"] == 1

    response = client.get("/cached?param=2")
    assert response.json()["count"] == 2


def test_path_params_cache_key(test_app):
    """Параметры пути учитываются в ключе кэша"""
    cached_endpoints = {"/cached/{id}": 60}
    app = test_app(cached_endpoints)
    call_count = 0

    @app.get("/cached/{id}")
    async def get_cached(id: int):
        nonlocal call_count
        call_count += 1
        return {"count": call_count, "id": id}

    client = TestClient(app)

    client.get("/cached/1")
    response = client.get("/cached/1")
    assert response.json()["count"] == 1

    response = client.get("/cached/2")
    assert response.json()["count"] == 2


def test_non_get_requests_not_cached(test_app):
    """Некэшируемые методы (POST) не сохраняются"""
    cached_endpoints = {"/cached": 60}
    app = test_app(cached_endpoints)
    call_count = 0

    @app.post("/cached")
    async def post_cached():
        nonlocal call_count
        call_count += 1
        return {"count": call_count}

    client = TestClient(app)

    client.post("/cached")
    response = client.post("/cached")
    assert response.json()["count"] == 2


def test_non_cached_endpoint(test_app):
    """Некэшируемые эндпоинты игнорируются"""
    cached_endpoints = {"/cached": 60}
    app = test_app(cached_endpoints)
    call_count = 0

    @app.get("/not-cached")
    async def get_not_cached():
        nonlocal call_count
        call_count += 1
        return {"count": call_count}

    client = TestClient(app)

    client.get("/not-cached")
    response = client.get("/not-cached")
    assert response.json()["count"] == 2


# Тест: ошибки при чтении/записи кэша не ломают запрос
@pytest.mark.asyncio
async def test_cache_errors_handled():
    """Ошибки при чтении/записи кэша не ломают запрос"""
    app = FastAPI()
    mock_cache = AsyncMock()
    mock_cache.get.side_effect = Exception("Read error")
    mock_cache.set.side_effect = Exception("Write error")

    app.add_middleware(
        CacheMiddleware, cache=mock_cache, cached_endpoints={"/cached": 60}
    )

    @app.get("/cached")
    async def get_cached():
        return {"message": "OK"}

    client = TestClient(app)

    response = client.get("/cached")
    assert response.status_code == 200

    response = client.get("/cached")
    assert response.status_code == 200
