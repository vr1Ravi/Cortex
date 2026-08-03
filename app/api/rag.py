"""RAG endpoint — ask a question across all your documents."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, rate_limit
from app.core.database import get_db
from app.schemas.rag import Citation, RagRequest, RagResponse
from app.services import rag as rag_service
from app.services import rag_lc as rag_lc_service

router = APIRouter(prefix="/rag", tags=["rag"])

SessionDep = Annotated[AsyncSession, Depends(get_db)]

@router.post("/ask", response_model=RagResponse, dependencies=[Depends(rate_limit)])
async def rag_ask(
    body: RagRequest,
    session: SessionDep,
    current_user: CurrentUser
    ) -> RagResponse:
    answer, chunks = await rag_service.answer_with_rag(
        session,
        body.question,
        current_user.id,
        body.k
        )
    return RagResponse(
        answer=answer,
        citation=[Citation(document_id=c.document_id, chunk_index=c.chunk_index) for c in chunks]
    )

@router.post("/ask-lc", response_model=RagResponse, dependencies=[Depends(rate_limit)])
async def rag_ask_lc(
    body: RagRequest,
    session: SessionDep,
    current_user: CurrentUser
) -> RagResponse:
    """Same RAG, built with LangChain LCEL — for comparison with /ask."""
    answer, rows = await rag_lc_service.answer_with_rag_lc(
        session,
        body.question,
        current_user.id,
        body.k
    )
    return RagResponse(
        answer=answer,
        citation=[Citation(document_id=c.document_id, chunk_index=c.chunk_index) for c, _ in rows]
        )