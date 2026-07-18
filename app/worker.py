"""Celery app + background tasks."""

import time

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "cortex",
    broker=settings.celery_broker_url,   # where tasks are pushed/pulled
    backend=settings.celery_result_backend   # where results are stored
)

@celery_app.task
def process_document(doc_id: int, content: str) -> dict:
    """Simulate SLOW document processing (later: real parsing + embeddings)."""
    time.sleep(5)
    return {
        "doc_id": doc_id,
        "word_count": len(content.split()),
        "status": "processed"
    }