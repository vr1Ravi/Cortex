"""Caching demo — cache-aside pattern with Redis."""

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.api.deps import rate_limit
from app.core.redis_client import redis_client

router = APIRouter(prefix="/demo", tags=["demo"])

@router.get("/expensive/{n}")
async def expensive_calc(n: int) -> dict:
    cache_key = f"expensive:{n}"

    #1. Check the cache (HIT ?)
    cached = await redis_client.get(cache_key)

    if cached is not None:
        return {"result": int(cached), "source": "cache"}
    
    #2. Cache MISS -> do the "expensive" work
    await asyncio.sleep(2)    # pretend this is slow
    result = n * n

    #3. Store in cache with a 30s TTL, then return
    await redis_client.set(cache_key, result, ex=30)
    return {"result": result, "source": "computed"}


@router.get("/limited", dependencies=[Depends(rate_limit)])
async def limited() -> dict:
    return {"message": "You got through!"}

@router.websocket("/ws/echo")
async def ws_echo(websocket: WebSocket) -> None:
    await websocket.accept()      # complete the handshake — connection now open

    try:
        while True:                                    # loop stays alive for the whole connection
            msg = await websocket.receive_text()       # wait for a message FROM the client
            await websocket.send_text(f"echo: {msg}")  # push one back
    except WebSocketDisconnect:
        pass    # client closed the pipe — exit cleanly

@router.get("/stream")
async def stream_tokens() -> StreamingResponse:
    async def event_generator():
        words = "Streaming tokens one by one just like an LLM".split()
        for word in words:
            yield f"data: {word}\n\n"
            await asyncio.sleep(0.3)
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")