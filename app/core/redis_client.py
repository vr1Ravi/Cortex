"""Async Redis client (for caching, rate limiting — NOT the Celery broker)."""


import redis.asyncio as redis

from app.core.config import settings

# db 1 keeps this separate from Celery's broker/backend on db 0.


redis_client = redis.from_url(settings.redis_url, decode_responses=True)