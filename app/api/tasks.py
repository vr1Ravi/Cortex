"""Task endpoints — enqueue background work and poll its status."""

from celery.result import AsyncResult
from fastapi import APIRouter, status
from pydantic import BaseModel

from app.worker import celery_app, process_document

router = APIRouter(prefix="/tasks", tags=["tasks"])

class ProcessRequest(BaseModel):
    doc_id: int
    content: str

class TaskCreated(BaseModel):
    task_id: str

class TaskStatus(BaseModel):
    task_id: str
    status: str
    result: dict | None = None


@router.post("/process-document", response_model=TaskCreated, status_code=status.HTTP_202_ACCEPTED)
async def enqueue_processing(body: ProcessRequest) -> TaskCreated:
    task = process_document.delay(body.doc_id, body.content)  # push to queue, returns instantly
    return TaskCreated(task_id=task.id)

@router.get("/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str) -> TaskStatus:
    res = AsyncResult(task_id, app=celery_app)
    return TaskStatus(
        task_id=task_id,
        status=res.status,    # PENDING / STARTED / SUCCESS / FAILURE
        result=res.result if res.ready() and res.successful() else None,
    )