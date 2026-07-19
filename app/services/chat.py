"""Chat service — talks to Gemini."""

import logging
from collections.abc import AsyncIterator

from google.genai import types

from app.core.config import settings
from app.core.llm import gemini, generate

SYSTEM_INSTRUCTION = (
    "You are Cortex, a concise and helpful knowledge assistant. "
    "Answer clearly and directly. If you don't know, say so."
)
logger = logging.getLogger("cortex.llm")
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
TRANSIENT_CODES = {429, 500, 503}   # worth retrying; NOT 400/401/403


async def generate_reply(message: str) -> str:
    response = await generate(
        contents=message,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
    )
    return response.text

async def stream_reply(message: str) -> AsyncIterator[str]:
    """Yield Gemini's reply chunk-by-chunk as it's generated."""
    async for chunk in await gemini.aio.models.generate_content_stream(
        model=settings.gemini_model,
        contents=message
    ):
        if chunk.text:      # some chunks can be empty — skip them
            yield chunk.text
