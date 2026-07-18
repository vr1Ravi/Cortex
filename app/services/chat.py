"""Chat service — talks to Gemini."""

from app.core.config import settings
from app.core.llm import gemini


async def generate_reply(message: str) -> str:
    response = await gemini.aio.models.generate_content(
        model=settings.gemini_model,
        contents=message
    )
    return response.text