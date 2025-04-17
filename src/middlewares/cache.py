import re
from typing import Dict, List, Tuple

from aiocache import Cache  # type:ignore[import-untyped]
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, _StreamingResponse

from ..logger import logger


class CacheMiddleware(BaseHTTPMiddleware):
    """Кэширующий middleware"""

    _cache: Cache
    _cached_patterns: List[Tuple[re.Pattern, int]]
    _max_size: int

    def __init__(
        self,
        app: FastAPI,
        cache: Cache,
        cached_endpoints: Dict[str, int],
        max_size: int = 0,
    ):
        super().__init__(app)
        self._cache = cache
        self._cached_patterns = [
            (self.path_mask_to_regex(mask), ttl)
            for mask, ttl in cached_endpoints.items()
        ]
        self._max_size = max_size
        logger.debug("Cache initialized")

    @staticmethod
    def path_mask_to_regex(path_mask: str) -> re.Pattern:
        """Создать регулярное выражение на основе маски:

        Пример использования:
        `/v1/notifications/` -> `^/v1/notifications/?$`
        `/v1/notifications/{notification_id}` -> `^/v1/notifications/[^/]+/?$`
        `/v1/notifications/{notification_id}/status` -> `^/v1/notifications/[^/]+/status/?$`
        """
        segments = path_mask.strip("/").split("/")
        regex_segments = []
        for segment in segments:
            if segment.startswith("{") and segment.endswith("}"):
                regex_segments.append(r"[^/]+")
            else:
                regex_segments.append(re.escape(segment))
        return re.compile(f"^/{'/'.join(regex_segments)}/?$")

    async def get_matching_ttl(self, path: str) -> int | None:
        """Поиск соответствия по паттернам"""
        for pattern, ttl in self._cached_patterns:
            if pattern.match(path):
                return ttl
        return None

    async def dispatch(self, request: Request, call_next):
        """Обработчик запросов"""
        if request.method != "GET":
            return await call_next(request)

        path_ttl = await self.get_matching_ttl(request.url.path)
        if path_ttl is None:
            return await call_next(request)

        key = f"{request.url.path}?{request.query_params}"

        logger.debug(f"Request key: {key}")

        try:
            cached_data = await self._cache.get(key)
            if cached_data is not None:
                logger.debug(f"Used cached data for endpoint: {key}")
                return Response(**cached_data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        response = await call_next(request)

        if 200 <= response.status_code < 300:
            try:
                if isinstance(response, _StreamingResponse):
                    content = b""
                    async for chunk in response.body_iterator:
                        if self._max_size != 0 and len(content) > self._max_size:
                            logger.warning(f"Content size more than: {self._max_size}")
                            raise Exception()
                        content += chunk  # type:ignore[operator]
                    response = Response(
                        content=content,
                        status_code=response.status_code,
                        headers=dict(response.headers),
                        media_type=response.media_type,
                    )
                cache_data = {
                    "content": response.body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                }
                await self._cache.set(key, cache_data, ttl=path_ttl)
                logger.debug(f"Request saved with key: {key}")
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
        return response
