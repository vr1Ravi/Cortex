"""Celery app + background tasks."""

import time

from celery import Celery

celery_app = Celery(
    "cortex",
    broker="redis://localhost:6379/0",   # where tasks are pushed/pulled
    backend="redis://localhost:6379/0"   # where results are stored
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