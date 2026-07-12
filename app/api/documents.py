"""Document endpoints — now owned by and scoped to the authenticated user."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
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

async def get_owned_document_or_404(
        doc_id: int,
        session: SessionDep,
        current_user: CurrentUser
) -> Document:
    """Fetch a document that MUST exist (404) and MUST belong to the caller (403)."""
    doc = await document_repo.get_by_id(session, doc_id)
    if doc is None:
        raise DocumentNotFoundError(doc_id)
    if doc.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this document"
        )
    return doc


# --- Endpoints (note: paths are RELATIVE to the router's /documents prefix) ---


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    doc: DocumentCreate, 
    session: SessionDep, 
    current_user: CurrentUser
    ) -> Document:
    return await document_repo.create(session, doc, owner_id=current_user.id)


@router.put("/{doc_id}", response_model=DocumentResponse, summary="Update a document")
async def update_document(
    update: DocumentUpdate,
    session: SessionDep,
    existing: Annotated[Document, Depends(get_owned_document_or_404)]
) -> DocumentResponse:
    return await document_repo.update(session, existing, update)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a document")
async def delete_document(
    session: SessionDep,
    existing: Annotated[Document, Depends(get_owned_document_or_404)],
) -> None:
    await document_repo.delete(session, existing)


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc: Annotated[Document, Depends(get_owned_document_or_404)],
) -> DocumentResponse:
    return doc


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    session: SessionDep,
    current_user: CurrentUser,
    pagination: Annotated[dict, Depends(pagination_params)],
) -> list[DocumentResponse]:
    return await document_repo.list_all(
        session,
        owner_id=current_user.id,
        skip=pagination["skip"], 
        limit=pagination["limit"]
        )
