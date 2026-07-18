"""Chat service — talks to Gemini."""

from collections.abc import AsyncIterator

from google.genai import types

from app.core.config import settings
from app.core.llm import gemini

SYSTEM_INSTRUCTION = (
    "You are Cortex, a concise and helpful knowledge assistant. "
    "Answer clearly and directly. If you don't know, say so."
)

async def generate_reply(message: str) -> str:
    response = await gemini.aio.models.generate_content(
        model=settings.gemini_model,
        contents=message,
        config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)
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
