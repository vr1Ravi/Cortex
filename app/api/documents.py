"""Document endpoints — now owned by and scoped to the authenticated user."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, rate_limit
from app.core.database import get_db
from app.core.exceptions import DocumentNotFoundError
from app.models.document import Document
from app.repositories import document as document_repo
from app.schemas.analysis import DocumentAnalysis
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.schemas.qa import AskRequest, AskResponse
from app.schemas.search import SearchRequest, SearchResult
from app.services import analysis as analysis_service
from app.services import qa as qa_service
from app.services import retrieval as retrieval_service
from app.worker import ingest_document_task

MAX_UPLOAD_BYTES = 1_000_000   # 1 MB
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
    created =  await document_repo.create(session, doc, owner_id=current_user.id)
    ingest_document_task.delay(created.id)   # enqueue; worker ingests in the background
    return created


@router.put("/{doc_id}", response_model=DocumentResponse, summary="Update a document")
async def update_document(
    update: DocumentUpdate,
    session: SessionDep,
    existing: Annotated[Document, Depends(get_owned_document_or_404)]
) -> DocumentResponse:
    updated = await document_repo.update(session, existing, update)
    ingest_document_task.delay(updated.id)
    return updated


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

@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    session: SessionDep,
    current_user: CurrentUser,
    file: UploadFile
) -> Document:
    content_bytes = await file.read()

    if len(content_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status.HTTP_413, "File too large (max 1 MB)")
    try:
        content = content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File must be UTF-8 text")
    if not content.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "File is empty")
    
    data = DocumentCreate(title=(file.filename or "untitled")[:200], content=content, tags=[])
    created =  await document_repo.create(session, data, owner_id=current_user.id)
    ingest_document_task.delay(created.id)
    return created

@router.post(
    "/{doc_id}/analyze",
    response_model=DocumentAnalysis,
    dependencies=[Depends(rate_limit)]
)
async def analyze_document(
    doc: Annotated[Document, Depends(get_owned_document_or_404)],
) -> DocumentAnalysis:
     """AI-analyze one of the user's documents into structured data."""
     return await analysis_service.analyze_document(doc.content)


@router.post("/{doc_id}/ask", response_model=AskResponse, dependencies=[Depends(rate_limit)])
async def ask_document(
    body: AskRequest,
    doc: Annotated[Document, Depends(get_owned_document_or_404)],
) -> AskResponse:
    """Ask a question about one of your documents — answered from its content."""
    answer = await qa_service.answer_from_document(body.question, doc.content)
    return AskResponse(answer=answer)

@router.post(
        "/{doc_id}/ingest",
        status_code=status.HTTP_202_ACCEPTED,
        dependencies=[Depends(rate_limit)]
        )
async def ingest_document(
    doc: Annotated[Document, Depends(get_owned_document_or_404)]
) -> dict:
    task = ingest_document_task.delay(doc.id)
    return {"task_id": task.id, "document_id": doc.id,  "status": "queued"}

@router.post("/search", response_model=list[SearchResult], dependencies=[Depends(rate_limit)])
async def search_document(
    body: SearchRequest, session: SessionDep, current_user: CurrentUser
) -> list[SearchResult]:
    rows = await retrieval_service.retrieve_chunks(session, body.query, current_user.id, body.k)
    return [
        SearchResult(
            document_id=c.document_id, chunk_index=c.chunk_index, content=c.content, distance=dist
        )
        for c, dist in rows
    ]