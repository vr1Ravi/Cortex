"""Chat endpoint — ask Gemini a question."""

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse  # add import

from app.api.deps import CurrentUser, rate_limit
from app.core.config import settings
from app.schemas.chat import ChastResponse, ChatRequest
from app.services import chat as chat_service

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChastResponse, dependencies=[Depends(rate_limit)])
async def chat(body: ChatRequest, current_user: CurrentUser) -> ChastResponse:
    reply = await chat_service.generate_reply(body.message)
    return ChastResponse(reply=reply, model=settings.gemini_model)


@router.post("/stream", dependencies=[Depends(rate_limit)])
async def chat_stream(body: ChatRequest, current_user: CurrentUser) -> StreamingResponse:
    async def event_generator():
        async for token in chat_service.stream_reply(body.message):
            yield f"data: {json.dumps(token)}\n\n" # SSE fram. JSON-encoded
        yield "data: [DONE]\n\n"                   # signal the end
    return StreamingResponse(event_generator(), media_type="text/event-stream")