"""Celery app + background tasks."""

import asyncio
import time

from celery import Celery

from app.core.config import settings
from app.core.database import async_session_maker, engine
from app.repositories import document as document_repo
from app.services.ingestion import insert_document

celery_app = Celery(
    "cortex",
    broker=settings.celery_broker_url,   # where tasks are pushed/pulled
    backend=settings.celery_result_backend   # where results are stored
)
async def _ingest_async(doc_id: int) -> int:
    """The real (async) work — run inside the sync task via asyncio.run()."""
    try:
        async with async_session_maker() as session: # our OWN session (no get_db here)
            doc = await document_repo.get_by_id(session, doc_id)
            if doc is None:                         # deleted before the worker got to it
                return 0
            return await insert_document(session, doc_id, doc.content)
    finally:
        # Connections are bound to the loop that made them. asyncio.run() uses a
        # FRESH loop each task, so drop the pooled connections or the next task
        # reuses one tied to a dead loop → "Future attached to a different loop".
        await engine.dispose()

@celery_app.task(name="ingest_document")
def ingest_document_task(doc_id: int) -> dict:
    """Chunk + embed + store a document's content, in the background."""
    count = asyncio.run(_ingest_async(doc_id))
    return {"doc_id": doc_id, "chunks_created": count}


@celery_app.task
def process_document(doc_id: int, content: str) -> dict:
    """Simulate SLOW document processing (later: real parsing + embeddings)."""
    time.sleep(5)
    return {
        "doc_id": doc_id,
        "word_count": len(content.split()),
        "status": "processed"
    }