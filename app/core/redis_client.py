"""Async Redis client (for caching, rate limiting — NOT the Celery broker)."""


import redis.asyncio as redis

# db 1 keeps this separate from Celery's broker/backend on db 0.
REDIS_URL = "redis://localhost:6379/1"

redis_client = redis.from_url(REDIS_URL, decode_responses=True)