"""Document endpoints — grouped in their own router."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.exceptions import DocumentNotFoundError
from app.schemas.document import DocumentCreate, DocumentResponse

router = APIRouter(prefix="/documents", tags=["documents"])

# --- Fake in-memory "database" (real DB comes in Phase 2) ---
_documents: dict[int, DocumentResponse] = {}
_next_id: int = 1

# --- Dependencies ---
def pagination_params(skip: int = 0, limit: int = 10) -> dict:
    return {"skip": skip, "limit": limit}

def get_document_or_404(doc_id: int) -> DocumentResponse:
    doc = _documents.get(doc_id)
    if doc is None:
        raise DocumentNotFoundError(doc_id)
    return doc

# --- Endpoints (note: paths are RELATIVE to the router's /documents prefix) ---

@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(doc: DocumentCreate) -> DocumentResponse:
    global _next_id
    doc_id = _next_id
    _next_id += 1
    stored = DocumentResponse(
        id=doc_id,
        word_count=len(doc.content.split()),
        created_at=datetime.now(timezone.utc),
        **doc.model_dump(),
    )
    _documents[doc_id] = stored
    return stored

@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc: Annotated[DocumentResponse, Depends(get_document_or_404)]
) -> DocumentResponse:
    return doc

@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    pagination: Annotated[dict, Depends(pagination_params)],
) -> list[DocumentResponse]:
    all_docs = list(_documents.values())
    return all_docs[pagination["skip"] : pagination["skip"] + pagination["limit"]]