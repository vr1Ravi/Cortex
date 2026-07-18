"""Chat endpoint — ask Gemini a question."""

from fastapi import APIRouter, Depends

from app.api.deps import CurrentUser, rate_limit
from app.core.config import settings
from app.schemas.chat import ChastResponse, ChatRequest
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChastResponse, dependencies=[Depends(rate_limit)])
async def chat(body: ChatRequest, current_user: CurrentUser) -> ChastResponse:
    reply = await chat_service.generate_reply(body.message)
    return ChastResponse(reply=reply, model=settings.gemini_model)