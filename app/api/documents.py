"""Document endpoints — now backed by PostgreSQL via the repository."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import DocumentNotFoundError
from app.models.document import Document
from app.repositories import document as document_repo
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate

router = APIRouter(prefix="/documents", tags=["documents"])

# A reusable alias so we don't retype the session dependency everywhere.
SessionDep = Annotated[AsyncSession, Depends(get_db)]


# --- Dependencies ---
def pagination_params(skip: int = 0, limit: int = 10) -> dict:
    return {"skip": skip, "limit": limit}


async def get_document_or_404(doc_id: int, session: SessionDep) -> Document:
    """Fetch a document from the DB, or raise the domain 404. Now uses the session."""

    doc = await document_repo.get_by_id(session, doc_id)
    if doc is None:
        raise DocumentNotFoundError(doc_id)
    return doc


# --- Endpoints (note: paths are RELATIVE to the router's /documents prefix) ---


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(doc: DocumentCreate, session: SessionDep) -> Document:
    return await document_repo.create(session, doc)


@router.put("/{doc_id}", response_model=DocumentResponse, summary="Update a document")
async def update_document(
    update: DocumentUpdate,
    session: SessionDep,
    existing: Annotated[Document, Depends(get_document_or_404)]
) -> DocumentResponse:
    return await document_repo.update(session, existing, update)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document")
async def delete_document(
    session: SessionDep,
    existing: Annotated[Document, Depends(get_document_or_404)],
) -> None:
    await document_repo.delete(session, existing)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc: Annotated[Document, Depends(get_document_or_404)],
) -> DocumentResponse:
    return doc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: SessionDep,
    pagination: Annotated[dict, Depends(pagination_params)],
) -> list[DocumentResponse]:
    return await document_repo.list_all(session, pagination["skip"], pagination["limit"])
