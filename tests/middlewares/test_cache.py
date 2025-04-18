from unittest.mock import AsyncMock

import pytest
from aiocache import Cache
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.middlewares.cache import CacheMiddleware


@pytest.fixture
def test_app():
    """Создать тестовое приложение с подключенным CacheMiddleware"""

    def _test_app(cached_endpoints):
        app = FastAPI()
        cache = Cache(Cache.MEMORY)
        app.add_middleware(
            CacheMiddleware, cache=cache, cached_endpoints=cached_endpoints
        )
        return app

    return _test_app


def test_get_cached_endpoint_returns_cached_response(test_app):
    """Тест возврата закэшированного ответа для GET-запроса к кэшируемому эндпоинту"""
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


def test_different_query_params_create_different_cache_keys(test_app):
    """Тест создания разных ключей кэша для запросов с разными query-параметрами"""
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


def test_different_path_params_create_different_cache_keys(test_app):
    """Тест создания разных ключей кэша для запросов с разными path-параметрами"""
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


def test_post_requests_are_not_cached(test_app):
    """Тест отсутствия кэширования POST запросов"""
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


def test_non_cached_endpoint_always_executes(test_app):
    """Тест выполнения запросов к некэшируемым эндпоинтам"""
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


@pytest.mark.asyncio
async def test_cache_errors_do_not_break_request_handling():
    """Тест обработки ошибок кэширования без прерывания запроса"""
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
